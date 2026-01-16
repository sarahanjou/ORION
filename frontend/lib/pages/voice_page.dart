import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:livekit_client/livekit_client.dart';
import 'package:permission_handler/permission_handler.dart';

import '../services/livekit_service.dart';
import '../services/audio_service.dart';
import '../widgets/error_screen.dart';
import '../widgets/loading_screen.dart';
import '../widgets/voice_interface.dart';

/// Page principale de l'interface vocale
class VoicePage extends StatefulWidget {
  const VoicePage({super.key});

  @override
  State<VoicePage> createState() => _VoicePageState();
}

class _VoicePageState extends State<VoicePage> with TickerProviderStateMixin {
  Room? _room;
  bool _isMuted = true;
  bool _connected = false;
  String? _errorMessage;

  Timer? _audioLevelTimer;
  Timer? _audioSubscriptionTimer;
  double _volume = 0.0;

  late AnimationController _waveAnimationController;

  // FocusNode pour capturer les événements clavier (barre d'espace)
  final FocusNode _focusNode = FocusNode();
  bool _isSpacePressed = false;

  @override
  void initState() {
    super.initState();
    debugPrint("VoicePage initState appelé");

    try {
      // Animation en boucle pour les ondes
      _waveAnimationController = AnimationController(
        vsync: this,
        duration: const Duration(seconds: 4),
      )..repeat();

      // Démarrer la connexion après un court délai pour s'assurer que le widget est monté
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _initAndConnect();
        }
      });
    } catch (e) {
      debugPrint("Erreur dans initState: $e");
      if (mounted) {
        setState(() {
          _errorMessage = "Erreur d'initialisation: $e";
        });
      }
    }
  }

  Future<void> _initAndConnect() async {
    // Demande de permission microphone sur mobile
    if (!kIsWeb) {
      var status = await Permission.microphone.request();
      if (!status.isGranted) return;
    }
    await connectToRoom();
  }

  Future<void> connectToRoom() async {
    try {
      setState(() {
        _errorMessage = null;
      });

      // Connexion à la Room LiveKit
      final room = await LiveKitService.connectToRoom();

      // Configurer le périphérique audio de sortie (optionnel)
      await LiveKitService.configureAudioOutputDevice(room);

      // S'abonner automatiquement aux tracks audio des participants distants (l'agent)
      _setupAudioSubscription(room);

      if (!mounted) return;

      setState(() {
        _room = room;
        _connected = true;
        _isMuted = true;
        _errorMessage = null;
      });

      _startAudioLevelTimer();
    } catch (e, stackTrace) {
      debugPrint("Erreur connexion: $e");
      debugPrint("Stack trace: $stackTrace");
      if (mounted) {
        setState(() {
          _connected = false;
          _errorMessage =
              "Erreur de connexion: ${e.toString()}\n\nVérifiez que:\n- Le serveur distant est accessible\n- LiveKit est accessible\n- Votre connexion internet fonctionne";
        });
      }
    }
  }

  void _setupAudioSubscription(Room room) {
    // Timer périodique pour vérifier et s'abonner aux nouveaux tracks
    _audioSubscriptionTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted || _room == null) {
        timer.cancel();
        return;
      }

      debugPrint("Vérification des participants distants (${room.remoteParticipants.length})");
      for (final participant in room.remoteParticipants.values) {
        LiveKitService.subscribeAndEnableAudioTracks(
          participant,
          (track, identity) {
            // Callback quand un track est prêt
            debugPrint("Track prêt pour $identity");
          },
        );
      }
    });

    // S'abonner immédiatement aux participants déjà connectés
    debugPrint("Participants déjà connectés: ${room.remoteParticipants.length}");
    for (final participant in room.remoteParticipants.values) {
      LiveKitService.subscribeAndEnableAudioTracks(
        participant,
        (track, identity) {
          debugPrint("Track prêt pour $identity");
        },
      );
    }
  }

  void toggleMute() async {
    if (_room?.localParticipant == null) return;

    // Sur le web, l'interaction utilisateur débloque l'autoplay audio
    if (kIsWeb && _room != null) {
      AudioService.reactivateAudioTracksAfterInteraction(_room!);
      await Future.delayed(const Duration(milliseconds: 100));
    }

    final shouldEnable = _isMuted; // Si mute est true, on veut activer (true)
    await _room!.localParticipant!.setMicrophoneEnabled(shouldEnable);

    if (!mounted) return;
    setState(() {
      _isMuted = !shouldEnable;
    });
  }

  void _startAudioLevelTimer() {
    _audioLevelTimer?.cancel();
    // Timer pour récupérer le volume et animer les cercles
    _audioLevelTimer = Timer.periodic(const Duration(milliseconds: 100), (timer) {
      _updateVolumeFromLiveKit();
    });
  }

  void _updateVolumeFromLiveKit() {
    if (_room?.localParticipant != null && mounted) {
      final double newVolume = _room!.localParticipant!.audioLevel;
      setState(() {
        // Lissage de la valeur pour fluidifier l'animation
        _volume = (_volume * 0.7) + (newVolume * 0.3);
      });
    }
  }

  /// Gère le push-to-talk avec la barre d'espace
  void _handleSpacePress(bool isPressed) async {
    if (_room?.localParticipant == null || !_connected) return;

    setState(() {
      _isSpacePressed = isPressed;
    });

    // Activer/désactiver le micro selon l'état de la barre d'espace
    bool shouldEnable = isPressed; // Si espace pressé = micro activé
    await _room!.localParticipant!.setMicrophoneEnabled(shouldEnable);

    // Sur le web, forcer la lecture audio lors de la première interaction
    if (isPressed && kIsWeb && _room != null) {
      AudioService.reactivateAudioTracksAfterInteraction(_room!);
    }

    // Mettre à jour l'état du mute pour l'affichage
    if (mounted) {
      setState(() {
        _isMuted = !shouldEnable;
      });
    }
  }

  @override
  void dispose() {
    _audioLevelTimer?.cancel();
    _audioSubscriptionTimer?.cancel();
    _waveAnimationController.dispose();
    _focusNode.dispose();
    _room?.disconnect();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    try {
      return KeyboardListener(
        focusNode: _focusNode,
        autofocus: true,
        onKeyEvent: (KeyEvent event) {
          // Capturer uniquement la barre d'espace
          if (event.logicalKey == LogicalKeyboardKey.space) {
            if (event is KeyDownEvent && !_isSpacePressed) {
              // Barre d'espace appuyée = unmute
              _handleSpacePress(true);
            } else if (event is KeyUpEvent && _isSpacePressed) {
              // Barre d'espace relâchée = mute
              _handleSpacePress(false);
            }
          }
        },
        child: Container(
          decoration: BoxDecoration(
            color: Colors.black,
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [
                Colors.black,
                Colors.grey.shade900,
              ],
            ),
          ),
          child: Stack(
            children: [
              // Image de fond en arrière-plan (avec gestion d'erreur)
              Positioned.fill(
                child: Image.asset(
                  'assets/background.jpg',
                  fit: BoxFit.cover,
                  errorBuilder: (context, error, stackTrace) {
                    debugPrint("Erreur chargement image: $error");
                    return Container();
                  },
                ),
              ),
              // Contenu principal
              Scaffold(
                backgroundColor: Colors.transparent,
                body: SafeArea(
                  child: _errorMessage != null
                      ? ErrorScreen(
                          errorMessage: _errorMessage!,
                          onRetry: () {
                            setState(() {
                              _connected = false;
                              _errorMessage = null;
                            });
                            connectToRoom();
                          },
                        )
                      : !_connected
                          ? const LoadingScreen()
                          : VoiceInterface(
                              isMuted: _isMuted,
                              volume: _volume,
                              animationController: _waveAnimationController,
                              onMuteToggle: toggleMute,
                            ),
                ),
              ),
            ],
          ),
        ),
      );
    } catch (e, stackTrace) {
      // En cas d'erreur dans le build, afficher un écran d'erreur
      debugPrint("Erreur dans build: $e");
      debugPrint("Stack: $stackTrace");
      return Scaffold(
        backgroundColor: Colors.black,
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error, color: Colors.red, size: 64),
              const SizedBox(height: 20),
              Text(
                "Erreur: $e",
                style: const TextStyle(color: Colors.white),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      );
    }
  }
}
