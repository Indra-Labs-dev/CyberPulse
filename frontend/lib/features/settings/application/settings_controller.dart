import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _themeModeKey = 'cyberpulse_theme_mode';
const _notificationsEnabledKey = 'cyberpulse_notifications_enabled';

final sharedPreferencesProvider = FutureProvider<SharedPreferences>((ref) {
  return SharedPreferences.getInstance();
});

final themeModeProvider = StateNotifierProvider<ThemeModeController, ThemeMode>((ref) {
  return ThemeModeController(ref);
});

class ThemeModeController extends StateNotifier<ThemeMode> {
  ThemeModeController(this._ref) : super(ThemeMode.dark) {
    _restore();
  }

  final Ref _ref;

  Future<void> _restore() async {
    final prefs = await _ref.read(sharedPreferencesProvider.future);
    final value = prefs.getString(_themeModeKey);
    if (value == 'light') state = ThemeMode.light;
  }

  Future<void> toggle() async {
    state = state == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    final prefs = await _ref.read(sharedPreferencesProvider.future);
    await prefs.setString(_themeModeKey, state == ThemeMode.dark ? 'dark' : 'light');
  }
}

final notificationsEnabledProvider =
    StateNotifierProvider<NotificationsEnabledController, bool>((ref) {
  return NotificationsEnabledController(ref);
});

class NotificationsEnabledController extends StateNotifier<bool> {
  NotificationsEnabledController(this._ref) : super(true) {
    _restore();
  }

  final Ref _ref;

  Future<void> _restore() async {
    final prefs = await _ref.read(sharedPreferencesProvider.future);
    state = prefs.getBool(_notificationsEnabledKey) ?? true;
  }

  Future<void> setEnabled(bool enabled) async {
    state = enabled;
    final prefs = await _ref.read(sharedPreferencesProvider.future);
    await prefs.setBool(_notificationsEnabledKey, enabled);
  }
}

/// Mode Focus: when active, realtime alert toasts/native notifications are
/// suppressed so an analyst can work without interruption. Alerts are still
/// recorded in the Alert Center — nothing is lost, just silenced.
final focusModeProvider = StateProvider<bool>((ref) => false);
