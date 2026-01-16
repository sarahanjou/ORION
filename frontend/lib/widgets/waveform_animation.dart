import 'dart:math' as math;
import 'dart:ui';
import 'package:flutter/material.dart';

/// Custom painter pour dessiner l'animation des ondes audio
class WaveformRingPainter extends CustomPainter {
  final double volume;
  final double animationValue;

  WaveformRingPainter({
    required this.volume,
    required this.animationValue,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final baseRadius = math.max(size.width / 5.0, 125.0);
    final double maxAmplitude = size.width * 0.065;

    final double exponentialVolume = math.pow(volume, 0.45).toDouble();
    final double minAmplitudeFactor = 0.05;
    final double dynamicAmplitudeFactor = 1.0 - minAmplitudeFactor;

    final double currentAmplitude = maxAmplitude *
        (minAmplitudeFactor + (exponentialVolume * dynamicAmplitudeFactor));
    final double basePhase = animationValue * 2 * math.pi;

    // Anneau externe
    final paintDotsOuter = Paint()
      ..color = Colors.cyan.shade800.withOpacity(0.4)
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke
      ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 4.0);
    _drawRing(canvas, center, baseRadius * 1.08, currentAmplitude * 0.7,
        basePhase * 0.5, paintDotsOuter, 6);

    // Anneau principal
    final paintDotsMain = Paint()
      ..color = Colors.cyanAccent
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..maskFilter = const MaskFilter.blur(BlurStyle.solid, 3.0);
    _drawRing(canvas, center, baseRadius, currentAmplitude, basePhase,
        paintDotsMain, 6);

    // Anneau interne
    final paintDotsInner = Paint()
      ..color = Colors.cyan.shade200.withOpacity(0.6)
      ..strokeWidth = 1.2
      ..style = PaintingStyle.stroke;
    _drawRing(canvas, center, baseRadius * 0.88, currentAmplitude * 0.5,
        basePhase * -1.5, paintDotsInner, 8);
  }

  void _drawRing(Canvas canvas, Offset center, double baseRadius,
      double amplitude, double phase, Paint paint, double waveFrequency) {
    final List<Offset> points = [];
    final int pointCount = 400;

    for (int i = 0; i < pointCount; i++) {
      final double angle = (i / pointCount) * 2 * math.pi;
      final double distortion =
          math.sin((angle * waveFrequency) + phase) * amplitude;
      final double currentRadius = baseRadius + distortion;

      final x = center.dx + currentRadius * math.cos(angle);
      final y = center.dy + currentRadius * math.sin(angle);

      points.add(Offset(x, y));
    }

    canvas.drawPoints(PointMode.points, points, paint);
  }

  @override
  bool shouldRepaint(covariant WaveformRingPainter oldDelegate) {
    return volume != oldDelegate.volume ||
        animationValue != oldDelegate.animationValue;
  }
}

/// Widget animé affichant les ondes audio
class WaveformAnimation extends StatelessWidget {
  final double volume;
  final AnimationController animationController;

  const WaveformAnimation({
    super.key,
    required this.volume,
    required this.animationController,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: animationController,
      builder: (context, child) {
        return LayoutBuilder(
          builder: (context, constraints) {
            final double paintSize = constraints.maxWidth;
            return CustomPaint(
              size: Size(paintSize, paintSize),
              painter: WaveformRingPainter(
                volume: volume,
                animationValue: animationController.value,
              ),
            );
          },
        );
      },
    );
  }
}
