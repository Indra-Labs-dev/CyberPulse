import 'package:flutter_local_notifications/flutter_local_notifications.dart';

/// Thin wrapper around flutter_local_notifications for desktop alert toasts.
///
/// flutter_local_notifications only ships native notification centers for
/// Linux and macOS among desktop targets; on Windows, alerts surface through
/// the in-app alert center and system tray instead (no native toast).
class NotificationService {
  NotificationService._internal();

  static final NotificationService instance = NotificationService._internal();

  final FlutterLocalNotificationsPlugin _plugin = FlutterLocalNotificationsPlugin();
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;

    const linuxSettings = LinuxInitializationSettings(defaultActionName: 'Ouvrir');
    const macSettings = DarwinInitializationSettings();

    const settings = InitializationSettings(
      linux: linuxSettings,
      macOS: macSettings,
    );

    try {
      await _plugin.initialize(settings);
    } catch (_) {
      // Notifications are best-effort: some desktop environments (e.g. CI,
      // sandboxed runners) may not support the native notification center.
    }
    _initialized = true;
  }

  Future<void> showAlert({required String title, required String body}) async {
    if (!_initialized) await init();
    try {
      await _plugin.show(
        DateTime.now().millisecondsSinceEpoch ~/ 1000,
        title,
        body,
        const NotificationDetails(
          linux: LinuxNotificationDetails(),
        ),
      );
    } catch (_) {
      // Swallow notification failures; the in-app alert center remains the
      // source of truth for alerts.
    }
  }
}
