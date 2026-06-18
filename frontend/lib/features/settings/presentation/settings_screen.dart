import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/app_config.dart';
import '../../../core/theme/app_colors.dart';
import '../../auth/application/auth_controller.dart';
import '../application/settings_controller.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeMode = ref.watch(themeModeProvider);
    final notificationsEnabled = ref.watch(notificationsEnabledProvider);
    final user = ref.watch(authControllerProvider).user;

    return Scaffold(
      appBar: AppBar(title: const Text('Paramètres')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          if (user != null)
            Card(
              child: ListTile(
                leading: const Icon(Icons.account_circle_outlined, color: AppColors.neonBlue),
                title: Text(user.username),
                subtitle: Text('${user.email} • ${user.role.name.toUpperCase()}'),
              ),
            ),
          const SizedBox(height: 16),
          Card(
            child: Column(
              children: [
                SwitchListTile(
                  title: const Text('Thème sombre SOC'),
                  subtitle: const Text('Désactiver pour le thème clair'),
                  value: themeMode == ThemeMode.dark,
                  onChanged: (_) => ref.read(themeModeProvider.notifier).toggle(),
                ),
                const Divider(height: 1, color: AppColors.borderColor),
                SwitchListTile(
                  title: const Text('Notifications desktop'),
                  subtitle: const Text('Alertes critiques et CVE en temps réel'),
                  value: notificationsEnabled,
                  onChanged: (value) =>
                      ref.read(notificationsEnabledProvider.notifier).setEnabled(value),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: ListTile(
              leading: const Icon(Icons.dns_outlined, color: AppColors.textSecondary),
              title: const Text('Backend API'),
              subtitle: Text(AppConfig.apiBaseUrl),
            ),
          ),
        ],
      ),
    );
  }
}
