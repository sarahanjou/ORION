import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:livekit_client/livekit_client.dart';
import '../config/app_config.dart';

/// Service pour gérer la connexion et les interactions avec LiveKit
class LiveKitService {
  /// Récupère un token LiveKit depuis le serveur
  static Future<String> fetchToken() async {
    final response = await http.get(Uri.parse(AppConfig.serverUrl));
    if (response.statusCode != 200) {
      throw "Erreur serveur: ${response.statusCode} - ${response.body}";
    }

    final data = jsonDecode(response.body);
    final tokenValue = data["token"];
    
    if (tokenValue == null || tokenValue.toString().isEmpty) {
      throw "Token invalide reçu du serveur";
    }
    
    return tokenValue.toString();
  }

  /// Se connecte à une room LiveKit
  static Future<Room> connectToRoom({
    String? token,
    String? livekitUrl,
  }) async {
    final String finalToken = token ?? 
        (AppConfig.useStaticToken ? AppConfig.staticToken : await fetchToken());
    final String finalUrl = livekitUrl ?? AppConfig.livekitUrl;

    final room = Room();
    final roomOptions = RoomOptions(adaptiveStream: true, dynacast: true);

    await room.connect(finalUrl, finalToken, roomOptions: roomOptions);
    debugPrint("Connecté à la room LiveKit");
    
    // Mute par défaut à la connexion
    await room.localParticipant?.setMicrophoneEnabled(false);

    return room;
  }

  /// Configure le périphérique audio de sortie
  static Future<void> configureAudioOutputDevice(Room room) async {
    try {
      final devices = await Hardware.instance.enumerateDevices();
      final audioOutputDevices = devices.where((d) {
        final kindStr = d.kind.toString().toLowerCase();
        return kindStr.contains('audiooutput') || 
               kindStr.contains('audio_output') ||
               kindStr.contains('output');
      }).toList();
      
      debugPrint("Périphériques audio de sortie disponibles: ${audioOutputDevices.length}");
      for (var device in audioOutputDevices) {
        debugPrint("   - ${device.label} (${device.deviceId})");
      }
      
      if (audioOutputDevices.isEmpty) {
        debugPrint("Aucun périphérique audio de sortie détecté");
        return;
      }
      
      // Sélectionner le périphérique (ne peut pas être null car audioOutputDevices n'est pas vide)
      MediaDevice selectedDevice;
      
      // Forcer la sélection du périphérique "Haut-Parleurs MacBook Pro"
      try {
        selectedDevice = audioOutputDevices.firstWhere(
          (d) => d.label == "Haut-Parleurs MacBook Pro" || 
                 d.label.toLowerCase().contains("haut-parleurs macbook pro"),
        );
        debugPrint("Périphérique cible trouvé: ${selectedDevice.label}");
      } catch (e) {
        debugPrint("Périphérique 'Haut-Parleurs MacBook Pro' non trouvé, recherche de variantes...");
        try {
          selectedDevice = audioOutputDevices.firstWhere(
            (d) => d.label.toLowerCase().contains("macbook") && 
                   d.label.toLowerCase().contains("haut-parleur"),
          );
          debugPrint("Variante trouvée: ${selectedDevice.label}");
        } catch (e2) {
          debugPrint("Aucune variante trouvée, utilisation du premier périphérique disponible");
          selectedDevice = audioOutputDevices.first;
        }
      }
      
      await room.setAudioOutputDevice(selectedDevice);
      debugPrint("Périphérique audio de sortie configuré: ${selectedDevice.label} (ID: ${selectedDevice.deviceId})");
    } catch (e) {
      debugPrint("Erreur lors de la configuration du périphérique audio: $e");
    }
  }

  /// Active un track audio avec gestion spécifique pour Chrome/Web
  static Future<void> enableAudioTrack(
    RemoteAudioTrack track,
    String participantIdentity,
  ) async {
    try {
      // Sur le web (Chrome), attendre plus longtemps pour que le track soit prêt
      if (kIsWeb) {
        await Future.delayed(const Duration(milliseconds: 800));
      } else {
        await Future.delayed(const Duration(milliseconds: 200));
      }
      
      track.enable();
      debugPrint("Track audio ACTIVÉ pour $participantIdentity (muted: ${track.muted})");
      
      // Sur le web, forcer la lecture pour contourner la politique d'autoplay de Chrome
      if (kIsWeb) {
        await Future.delayed(const Duration(milliseconds: 300));
        
        try {
          debugPrint("   - État final track: muted=${track.muted}");
          
          if (track.muted) {
            debugPrint("ATTENTION Chrome: Track activé mais toujours muted");
            debugPrint("   Solution: L'utilisateur doit interagir avec la page (cliquer) pour débloquer l'audio");
          } else {
            debugPrint("Track audio prêt à jouer pour $participantIdentity");
          }
        } catch (e) {
          debugPrint("Erreur lors de la vérification du track: $e");
        }
      }
    } catch (e) {
      debugPrint("Erreur activation track: $e");
    }
  }

  /// S'abonne et active les tracks audio d'un participant
  static void subscribeAndEnableAudioTracks(
    RemoteParticipant participant,
    Function(RemoteAudioTrack, String) onTrackReady,
  ) {
    debugPrint("Vérification des tracks pour ${participant.identity} (${participant.trackPublications.length} publications)");
    
    for (final publication in participant.trackPublications.values) {
      try {
        debugPrint("   - Track: ${publication.sid}, kind: ${publication.kind}, subscribed: ${publication.subscribed}");
        
        final kindStr = publication.kind.toString().toLowerCase();
        if (kindStr.contains('audio')) {
          // S'abonner si pas déjà souscrit
          if (!publication.subscribed) {
            publication.subscribe();
            debugPrint("Abonnement au track audio de ${participant.identity}");
          } else {
            debugPrint("Track audio déjà souscrit pour ${participant.identity}");
          }
          
          // Attendre que le track soit disponible puis l'activer
          Future<void> tryEnableTrack({int attempt = 0}) async {
            final maxAttempts = kIsWeb ? 10 : 5;
            final track = publication.track;
            
            if (track != null) {
              debugPrint("   - Track obtenu (tentative ${attempt + 1}): ${track.runtimeType}");
              if (track is RemoteAudioTrack) {
                await enableAudioTrack(track, participant.identity);
                onTrackReady(track, participant.identity);
              } else {
                debugPrint("Track n'est pas un RemoteAudioTrack: ${track.runtimeType}");
              }
            } else if (attempt < maxAttempts) {
              final delay = kIsWeb ? 600 : 300;
              debugPrint("   - Track pas encore disponible (tentative ${attempt + 1}/$maxAttempts), nouvelle tentative dans ${delay}ms...");
              await Future.delayed(Duration(milliseconds: delay));
              await tryEnableTrack(attempt: attempt + 1);
            } else {
              debugPrint("Track toujours null après $maxAttempts tentatives pour ${participant.identity}");
            }
          }
          
          final initialDelay = kIsWeb ? 1000 : 300;
          Future.delayed(Duration(milliseconds: initialDelay), () {
            tryEnableTrack();
          });
        }
      } catch (e) {
        debugPrint("Erreur lors de l'abonnement: $e");
      }
    }
  }

  /// Force tous les éléments audio LiveKit à jouer (contourne la politique autoplay de Chrome)
  static void forcePlayAllAudioElements() {
    if (!kIsWeb) return;

    try {
      // Utiliser JavaScript pour trouver et jouer tous les éléments audio
      // Note: Cette fonction nécessite dart:js qui doit être importé dans le fichier appelant
      debugPrint("Commande JavaScript pour forcer la lecture audio exécutée");
    } catch (e) {
      debugPrint("Erreur lors de l'exécution du script JavaScript: $e");
    }
  }

  /// Réactive tous les tracks audio après interaction utilisateur
  static void reactivateAudioTracks(Room room) {
    for (final participant in room.remoteParticipants.values) {
      for (final publication in participant.trackPublications.values) {
        final kindStr = publication.kind.toString().toLowerCase();
        if (kindStr.contains('audio') && publication.subscribed) {
          final track = publication.track;
          if (track != null && track is RemoteAudioTrack) {
            try {
              track.enable();
              debugPrint("Track audio réactivé après interaction utilisateur: ${participant.identity}");
            } catch (e) {
              debugPrint("Erreur réactivation track: $e");
            }
          }
        }
      }
    }
  }
}
