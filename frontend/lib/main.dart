import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:window_manager/window_manager.dart';

import 'core/desktop/system_tray_service.dart';
import 'core/notifications/app_messenger.dart';
import 'core/notifications/notification_service.dart';
import 'core/theme/app_theme.dart';
import 'features/settings/application/settings_controller.dart';
import 'features/websocket/websocket_connection_provider.dart';
import 'routes/app_router.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
    await windowManager.ensureInitialized();
    const windowOptions = WindowOptions(
      size: Size(1440, 900),
      minimumSize: Size(1100, 700),
      center: true,
      title: 'CyberPulse — Centre de Veille Cybersécurité',
      backgroundColor: Colors.transparent,
    );
    await windowManager.waitUntilReadyToShow(windowOptions, () async {
      await windowManager.show();
      await windowManager.focus();
    });
  }

  await NotificationService.instance.init();

  runApp(const ProviderScope(child: CyberPulseApp()));

  if (Platform.isWindows || Platform.isLinux) {
    await SystemTrayService.instance.init();
  }
}

class CyberPulseApp extends ConsumerWidget {
  const CyberPulseApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Keeps the realtime WebSocket connected/disconnected in sync with auth.
    ref.watch(webSocketConnectionProvider);

    final router = ref.watch(routerProvider);
    final themeMode = ref.watch(themeModeProvider);

    return MaterialApp.router(
      title: 'CyberPulse',
      debugShowCheckedModeBanner: false,
      themeMode: themeMode,
      theme: AppTheme.light,
      darkTheme: AppTheme.dark,
      scaffoldMessengerKey: appMessengerKey,
      routerConfig: router,
    );
  }
}
