import 'package:dio/dio.dart';

import '../../../core/network/api_exception.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/storage/secure_storage_service.dart';
import '../../../models/auth_tokens.dart';
import '../../../models/user.dart';

class AuthService {
  AuthService(this._dioClient, this._storage);

  final DioClient _dioClient;
  final SecureStorageService _storage;

  Dio get _dio => _dioClient.dio;

  Future<User> register({
    required String username,
    required String email,
    required String password,
    UserRole role = UserRole.reader,
  }) async {
    try {
      final response = await _dio.post('/auth/register', data: {
        'username': username,
        'email': email,
        'password': password,
        'role': userRoleToString(role),
      });
      return User.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<AuthTokens> login({required String username, required String password}) async {
    try {
      final response = await _dio.post('/auth/login', data: {
        'username': username,
        'password': password,
      });
      final tokens = AuthTokens.fromJson(response.data as Map<String, dynamic>);
      await _storage.saveTokens(accessToken: tokens.accessToken, refreshToken: tokens.refreshToken);
      return tokens;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<User> getCurrentUser() async {
    try {
      final response = await _dio.get('/users/me');
      return User.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> logout() async {
    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken != null) {
      try {
        await _dio.post('/auth/logout', data: {'refresh_token': refreshToken});
      } on DioException {
        // best-effort revoke; local session is cleared regardless.
      }
    }
    await _storage.clear();
  }

  Future<bool> hasValidSession() async {
    final accessToken = await _storage.getAccessToken();
    return accessToken != null;
  }
}

class AuthException extends ApiException {
  AuthException(super.message, {super.statusCode});
}
