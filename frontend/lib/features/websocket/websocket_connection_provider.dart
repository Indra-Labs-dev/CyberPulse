import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/providers/core_providers.dart';
import '../auth/application/auth_controller.dart';
import '../auth/application/auth_state.dart';

/// Connects/disconnects the realtime WebSocket as the auth session changes.
final webSocketConnectionProvider = Provider<void>((ref) {
  final socket = ref.watch(webSocketServiceProvider);
  ref.listen<AuthState>(authControllerProvider, (previous, next) {
    if (next.isAuthenticated) {
      socket.connect();
    } else if (next.status == AuthStatus.unauthenticated) {
      socket.disconnect();
    }
  }, fireImmediately: true);
});
