import '../../../models/user.dart';

enum AuthStatus { unknown, authenticating, authenticated, unauthenticated, error }

class AuthState {
  const AuthState({required this.status, this.user, this.errorMessage});

  final AuthStatus status;
  final User? user;
  final String? errorMessage;

  const AuthState.unknown() : this(status: AuthStatus.unknown);

  factory AuthState.authenticated(User user) =>
      AuthState(status: AuthStatus.authenticated, user: user);

  factory AuthState.unauthenticated() => const AuthState(status: AuthStatus.unauthenticated);

  factory AuthState.authenticating() => const AuthState(status: AuthStatus.authenticating);

  factory AuthState.error(String message) =>
      AuthState(status: AuthStatus.error, errorMessage: message);

  bool get isAuthenticated => status == AuthStatus.authenticated && user != null;
}
