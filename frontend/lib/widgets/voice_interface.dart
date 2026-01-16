import 'package:flutter/material.dart';
import 'mute_button.dart';
import 'waveform_animation.dart';

/// Interface principale avec l'animation des ondes et le bouton mute
class VoiceInterface extends StatelessWidget {
  final bool isMuted;
  final double volume;
  final AnimationController animationController;
  final VoidCallback onMuteToggle;

  const VoiceInterface({
    super.key,
    required this.isMuted,
    required this.volume,
    required this.animationController,
    required this.onMuteToggle,
  });

  @override
  Widget build(BuildContext context) {
    final double displayVolume = isMuted ? 0.0 : volume;

    return Center(
      child: LayoutBuilder(
        builder: (context, constraints) {
          return Stack(
            alignment: Alignment.center,
            children: [
              // Animation Waveform
              WaveformAnimation(
                volume: displayVolume,
                animationController: animationController,
              ),

              // Bouton Mute
              MuteButton(
                isMuted: isMuted,
                onTap: onMuteToggle,
              ),
            ],
          );
        },
      ),
    );
  }
}
