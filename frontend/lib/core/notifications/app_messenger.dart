import 'package:flutter/material.dart';

import '../theme/app_colors.dart';

/// Global key used to surface in-app toast banners for realtime alerts.
///
/// This is the cross-platform fallback notification channel: native OS
/// notifications (via [NotificationService]) only cover Linux/macOS since
/// flutter_local_notifications has no Windows backend, so on Windows this
/// banner — combined with the system tray icon and the Alert Center — is
/// the visible "desktop notification" for a new alert.
final GlobalKey<ScaffoldMessengerState> appMessengerKey = GlobalKey<ScaffoldMessengerState>();

void showAppToast({required String title, required String body, Color accent = AppColors.alertRed}) {
  final messenger = appMessengerKey.currentState;
  if (messenger == null) return;

  messenger.showSnackBar(
    SnackBar(
      backgroundColor: AppColors.panelBlack,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: accent.withValues(alpha: 0.5)),
      ),
      content: Row(
        children: [
          Icon(Icons.notifications_active, color: accent, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(title, style: TextStyle(color: accent, fontWeight: FontWeight.bold)),
                Text(body, style: const TextStyle(color: AppColors.textPrimary, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
      duration: const Duration(seconds: 5),
    ),
  );
}
