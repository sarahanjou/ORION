import 'dart:js' as js;
import 'package:flutter/foundation.dart';
import 'package:livekit_client/livekit_client.dart';
import 'livekit_service.dart';

/// Service pour gérer l'audio et contourner les restrictions du navigateur
class AudioService {
  /// Force tous les éléments audio LiveKit à jouer (contourne la politique autoplay de Chrome)
  static void forcePlayAllAudioElements() {
    if (!kIsWeb) return;

    try {
      js.context.callMethod('eval', ['''
        (function() {
          console.log('Forcing all LiveKit audio elements to play...');

          const audioElements = document.querySelectorAll('audio[id^="livekit_audio"]');
          console.log('   Found ' + audioElements.length + ' LiveKit audio elements');

          audioElements.forEach(function(audio, index) {
            console.log('   - Audio element ' + (index + 1) + ': ' + audio.id);
            console.log('     paused: ' + audio.paused + ', muted: ' + audio.muted);

            if (audio.paused) {
              audio.play().then(function() {
                console.log('     Playing audio element ' + audio.id);
              }).catch(function(error) {
                console.error('     Failed to play ' + audio.id + ':', error);
              });
            } else {
              console.log('     Already playing');
            }
          });
        })();
      ''']);

      debugPrint("Commande JavaScript pour forcer la lecture audio exécutée");
    } catch (e) {
      debugPrint("Erreur lors de l'exécution du script JavaScript: $e");
    }
  }

  /// Réactive tous les tracks audio après interaction utilisateur
  static void reactivateAudioTracksAfterInteraction(Room room) {
    forcePlayAllAudioElements();
    LiveKitService.reactivateAudioTracks(room);
  }
}
