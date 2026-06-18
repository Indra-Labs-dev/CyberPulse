import 'package:flutter/material.dart';

/// CyberPulse SOC/SIEM color palette: deep black, neon blue, alert red, security green.
class AppColors {
  AppColors._();

  static const Color deepBlack = Color(0xFF0A0E14);
  static const Color panelBlack = Color(0xFF11161F);
  static const Color panelBlackAlt = Color(0xFF161C27);
  static const Color borderColor = Color(0xFF232B38);

  static const Color neonBlue = Color(0xFF00E5FF);
  static const Color neonBlueDim = Color(0xFF0090A8);

  static const Color alertRed = Color(0xFFFF3B5C);
  static const Color alertRedDim = Color(0xFF7A1F2C);

  static const Color securityGreen = Color(0xFF00FFA3);
  static const Color securityGreenDim = Color(0xFF0B8A5F);

  static const Color warningAmber = Color(0xFFFFB020);

  static const Color textPrimary = Color(0xFFE7ECF3);
  static const Color textSecondary = Color(0xFF8C99AC);
  static const Color textMuted = Color(0xFF5B6678);

  // Light theme counterparts
  static const Color lightBackground = Color(0xFFF4F6F9);
  static const Color lightSurface = Color(0xFFFFFFFF);
  static const Color lightBorder = Color(0xFFE0E4EA);
  static const Color lightTextPrimary = Color(0xFF12161F);
  static const Color lightTextSecondary = Color(0xFF505A6B);

  static Color severityColor(String severity) {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return alertRed;
      case 'HIGH':
        return const Color(0xFFFF7A45);
      case 'MEDIUM':
        return warningAmber;
      case 'LOW':
        return securityGreen;
      default:
        return textSecondary;
    }
  }
}
