import 'package:flutter/foundation.dart';
import 'package:livekit_client/livekit_client.dart';
import 'livekit_service.dart';

/// Service pour gérer l'audio et contourner les restrictions du navigateur
class AudioService {
  /// Force tous les éléments audio LiveKit à jouer (contourne la politique autoplay de Chrome)
  static void forcePlayAllAudioElements() {
    if (!kIsWeb) return;

    try {
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
