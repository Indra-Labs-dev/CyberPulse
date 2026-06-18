import 'dart:io';

import 'package:system_tray/system_tray.dart';
import 'package:window_manager/window_manager.dart';

/// Keeps a persistent CyberPulse icon in the system tray (Windows/Linux/macOS)
/// with quick actions to show/hide the main window or quit the app.
class SystemTrayService {
  SystemTrayService._internal();

  static final SystemTrayService instance = SystemTrayService._internal();

  final SystemTray _systemTray = SystemTray();
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;

    final iconPath = Platform.isWindows
        ? 'windows/runner/resources/app_icon.ico'
        : 'assets/images/logo.png';

    try {
      await _systemTray.initSystemTray(
        title: 'CyberPulse',
        iconPath: iconPath,
        toolTip: 'CyberPulse — Veille cybersécurité',
      );

      final menu = Menu();
      await menu.buildFrom([
        MenuItemLabel(label: 'Afficher CyberPulse', onClicked: (_) => windowManager.show()),
        MenuItemLabel(label: 'Masquer', onClicked: (_) => windowManager.hide()),
        MenuSeparator(),
        MenuItemLabel(label: 'Quitter', onClicked: (_) => windowManager.close()),
      ]);
      await _systemTray.setContextMenu(menu);

      // The plugin never shows the context menu on its own: a left click is
      // expected to toggle the window, and a right click must explicitly
      // trigger `popUpContextMenu()` (Windows convention; macOS/Linux tray
      // menus open on either click, so we show the menu there on left click
      // too and keep show-on-click for the window via double-click).
      _systemTray.registerSystemTrayEventHandler((eventName) {
        switch (eventName) {
          case kSystemTrayEventClick:
            if (Platform.isWindows) {
              windowManager.show();
            } else {
              _systemTray.popUpContextMenu();
            }
          case kSystemTrayEventRightClick:
            if (Platform.isWindows) {
              _systemTray.popUpContextMenu();
            } else {
              windowManager.show();
            }
          case kSystemTrayEventDoubleClick:
            windowManager.show();
        }
      });

      _initialized = true;
    } catch (_) {
      // System tray is best-effort: some Linux desktop environments lack
      // tray support entirely, which should not block app startup.
    }
  }
}
