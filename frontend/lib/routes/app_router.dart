import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/alerts/presentation/alerts_screen.dart';
import '../features/articles/presentation/article_reader_screen.dart';
import '../features/articles/presentation/articles_screen.dart';
import '../features/auth/application/auth_controller.dart';
import '../features/auth/application/auth_state.dart';
import '../features/auth/presentation/login_screen.dart';
import '../features/auth/presentation/register_screen.dart';
import '../features/cve/presentation/cve_detail_screen.dart';
import '../features/cve/presentation/cve_list_screen.dart';
import '../features/dashboard/presentation/dashboard_screen.dart';
import '../features/reports/presentation/report_preview_screen.dart';
import '../features/reports/presentation/reports_screen.dart';
import '../features/settings/presentation/settings_screen.dart';
import '../features/watchlist/presentation/watchlist_screen.dart';
import '../shared/app_shell.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    refreshListenable: _AuthRefreshListenable(ref),
    redirect: (context, state) {
      final authState = ref.read(authControllerProvider);
      final path = state.uri.path;
      final isAuthRoute = path == '/login' || path == '/register';

      if (authState.status == AuthStatus.unknown) return null;

      if (!authState.isAuthenticated && !isAuthRoute) return '/login';
      if (authState.isAuthenticated && isAuthRoute) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(path: '/dashboard', builder: (context, state) => const DashboardScreen()),
          GoRoute(
            path: '/cves',
            builder: (context, state) => const CveListScreen(),
            routes: [
              GoRoute(
                path: ':id',
                builder: (context, state) =>
                    CveDetailScreen(cveId: int.parse(state.pathParameters['id']!)),
              ),
            ],
          ),
          GoRoute(
            path: '/articles',
            builder: (context, state) => const ArticlesScreen(),
            routes: [
              GoRoute(
                path: ':id',
                builder: (context, state) =>
                    ArticleReaderScreen(articleId: int.parse(state.pathParameters['id']!)),
              ),
            ],
          ),
          GoRoute(path: '/watchlist', builder: (context, state) => const WatchlistScreen()),
          GoRoute(path: '/alerts', builder: (context, state) => const AlertsScreen()),
          GoRoute(
            path: '/reports',
            builder: (context, state) => const ReportsScreen(),
            routes: [
              GoRoute(
                path: 'preview',
                builder: (context, state) {
                  final extra = state.extra as Map<String, dynamic>;
                  return ReportPreviewScreen(
                    filePath: extra['path'] as String,
                    title: extra['title'] as String,
                  );
                },
              ),
            ],
          ),
          GoRoute(path: '/settings', builder: (context, state) => const SettingsScreen()),
        ],
      ),
    ],
  );
});

/// Bridges Riverpod's [AuthState] changes into a [Listenable] so GoRouter
/// re-evaluates its `redirect` callback whenever auth status changes.
class _AuthRefreshListenable extends ChangeNotifier {
  _AuthRefreshListenable(Ref ref) {
    ref.listen<AuthState>(authControllerProvider, (previous, next) {
      if (previous?.status != next.status) notifyListeners();
    });
  }
}
