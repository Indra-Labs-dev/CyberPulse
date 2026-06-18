import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/providers/core_providers.dart';
import '../../../models/user.dart';
import '../data/auth_service.dart';
import 'auth_state.dart';

final authServiceProvider = Provider<AuthService>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  final storage = ref.watch(secureStorageProvider);
  return AuthService(dioClient, storage);
});

final authControllerProvider = StateNotifierProvider<AuthController, AuthState>((ref) {
  return AuthController(ref);
});

class AuthController extends StateNotifier<AuthState> {
  AuthController(this._ref) : super(const AuthState.unknown()) {
    restoreSession();
  }

  final Ref _ref;

  AuthService get _service => _ref.read(authServiceProvider);

  Future<void> restoreSession() async {
    final hasSession = await _service.hasValidSession();
    if (!hasSession) {
      state = AuthState.unauthenticated();
      return;
    }
    try {
      final user = await _service.getCurrentUser();
      state = AuthState.authenticated(user);
    } catch (_) {
      state = AuthState.unauthenticated();
    }
  }

  Future<bool> login({required String username, required String password}) async {
    state = AuthState.authenticating();
    try {
      await _service.login(username: username, password: password);
      final user = await _service.getCurrentUser();
      state = AuthState.authenticated(user);
      return true;
    } on ApiException catch (e) {
      state = AuthState.error(e.message);
      return false;
    }
  }

  Future<bool> register({
    required String username,
    required String email,
    required String password,
    UserRole role = UserRole.reader,
  }) async {
    state = AuthState.authenticating();
    try {
      await _service.register(username: username, email: email, password: password, role: role);
      return await login(username: username, password: password);
    } on ApiException catch (e) {
      state = AuthState.error(e.message);
      return false;
    }
  }

  Future<void> logout() async {
    await _service.logout();
    state = AuthState.unauthenticated();
  }

  void forceLogout() {
    _ref.read(secureStorageProvider).clear();
    if (state.status != AuthStatus.unauthenticated) {
      state = AuthState.unauthenticated();
    }
  }
}
