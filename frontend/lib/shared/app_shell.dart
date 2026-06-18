import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../core/theme/app_colors.dart';
import '../features/alerts/application/alert_controller.dart';
import '../features/auth/application/auth_controller.dart';
import '../widgets/connection_status_indicator.dart';

class _NavItem {
  const _NavItem(this.label, this.icon, this.path);
  final String label;
  final IconData icon;
  final String path;
}

const _navItems = [
  _NavItem('Dashboard', Icons.dashboard_outlined, '/dashboard'),
  _NavItem('Veille CVE', Icons.bug_report_outlined, '/cves'),
  _NavItem('Articles & Blogs', Icons.rss_feed_outlined, '/articles'),
  _NavItem('Watchlist', Icons.visibility_outlined, '/watchlist'),
  _NavItem('Alertes', Icons.notifications_outlined, '/alerts'),
  _NavItem('Rapports', Icons.description_outlined, '/reports'),
  _NavItem('Paramètres', Icons.settings_outlined, '/settings'),
];

class AppShell extends ConsumerWidget {
  const AppShell({super.key, required this.child});

  final Widget child;

  int _indexForLocation(String location) {
    final index = _navItems.indexWhere((item) => location.startsWith(item.path));
    return index == -1 ? 0 : index;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final location = GoRouterState.of(context).uri.toString();
    final selectedIndex = _indexForLocation(location);
    final unacknowledged = ref.watch(unacknowledgedAlertCountProvider);
    final user = ref.watch(authControllerProvider).user;

    return Scaffold(
      body: Row(
        children: [
          NavigationRail(
            selectedIndex: selectedIndex,
            backgroundColor: AppColors.panelBlack,
            labelType: NavigationRailLabelType.all,
            leading: Padding(
              padding: const EdgeInsets.symmetric(vertical: 16),
              child: Column(
                children: [
                  Image.asset('assets/images/logo.png', width: 36, height: 36),
                  const SizedBox(height: 8),
                  const ConnectionStatusIndicator(),
                ],
              ),
            ),
            trailing: Expanded(
              child: Align(
                alignment: Alignment.bottomCenter,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: IconButton(
                    tooltip: 'Déconnexion (${user?.username ?? ''})',
                    icon: const Icon(Icons.logout, color: AppColors.textSecondary),
                    onPressed: () async {
                      await ref.read(authControllerProvider.notifier).logout();
                      if (context.mounted) context.go('/login');
                    },
                  ),
                ),
              ),
            ),
            onDestinationSelected: (index) => context.go(_navItems[index].path),
            destinations: _navItems.map((item) {
              final icon = item.path == '/alerts' && unacknowledged > 0
                  ? Badge(label: Text('$unacknowledged'), child: Icon(item.icon))
                  : Icon(item.icon);
              return NavigationRailDestination(
                icon: icon,
                selectedIcon: Icon(item.icon, color: AppColors.neonBlue),
                label: Text(item.label),
              );
            }).toList(),
          ),
          const VerticalDivider(width: 1, color: AppColors.borderColor),
          Expanded(child: child),
        ],
      ),
    );
  }
}
