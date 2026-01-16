import 'package:flutter/material.dart';

/// Bouton pour activer/désactiver le microphone avec animation
class MuteButton extends StatelessWidget {
  final bool isMuted;
  final VoidCallback onTap;

  const MuteButton({
    super.key,
    required this.isMuted,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    const double buttonSize = 150.0;
    const double iconSize = 60.0;
    const Color baseColor = Colors.cyanAccent;

    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: buttonSize,
        height: buttonSize,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: !isMuted
                ? [
                    // Actif : Effet Verre/Lumière
                    baseColor.withOpacity(0.3),
                    baseColor.withOpacity(0.05),
                  ]
                : [
                    // Inactif : Effet Mat Sombre
                    Colors.grey.shade800,
                    Colors.black54,
                  ],
          ),
          border: Border.all(
            color: !isMuted
                ? baseColor.withOpacity(0.5)
                : Colors.grey.shade600,
            width: 2,
          ),
          boxShadow: [
            BoxShadow(
              color: !isMuted
                  ? baseColor.withOpacity(0.3)
                  : Colors.black.withOpacity(0.5),
              blurRadius: !isMuted ? 30 : 10,
              spreadRadius: 2,
            ),
          ],
        ),
        child: Icon(
          isMuted ? Icons.mic_off_rounded : Icons.mic_rounded,
          color: Colors.white,
          size: iconSize,
        ),
      ),
    );
  }
}
