import 'package:dio/dio.dart';

import '../config/app_config.dart';
import '../storage/secure_storage_service.dart';
import 'api_exception.dart';

/// Builds the shared Dio instance used across all API services.
///
/// Handles:
/// - JWT injection on every request
/// - Automatic refresh-token retry on 401
/// - Centralized error -> [ApiException] mapping
class DioClient {
  DioClient(this._storage, {this.onSessionExpired}) {
    dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrlWithPrefix,
        connectTimeout: AppConfig.connectTimeout,
        receiveTimeout: AppConfig.receiveTimeout,
        contentType: 'application/json',
      ),
    );

    _refreshDio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrlWithPrefix,
        connectTimeout: AppConfig.connectTimeout,
      ),
    );

    dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _storage.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (DioException error, handler) async {
          final isAuthEndpoint = error.requestOptions.path.contains('/auth/');
          if (error.response?.statusCode == 401 && !isAuthEndpoint) {
            final retried = await _retryWithRefreshedToken(error);
            if (retried != null) {
              return handler.resolve(retried);
            }
            onSessionExpired?.call();
          }
          handler.next(error);
        },
      ),
    );
  }

  final SecureStorageService _storage;
  final void Function()? onSessionExpired;

  late final Dio dio;
  late final Dio _refreshDio;

  bool _isRefreshing = false;
  Future<String?>? _refreshFuture;

  Future<Response<dynamic>?> _retryWithRefreshedToken(DioException error) async {
    final refreshToken = await _storage.getRefreshToken();
    if (refreshToken == null) return null;

    if (!_isRefreshing) {
      _isRefreshing = true;
      _refreshFuture = _performRefresh(refreshToken);
    }

    final newAccessToken = await _refreshFuture;
    _isRefreshing = false;

    if (newAccessToken == null) return null;

    final requestOptions = error.requestOptions;
    requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';

    try {
      return await dio.fetch(requestOptions);
    } on DioException {
      return null;
    }
  }

  Future<String?> _performRefresh(String refreshToken) async {
    try {
      final response = await _refreshDio.post(
        '/auth/refresh',
        data: {'refresh_token': refreshToken},
      );
      final accessToken = response.data['access_token'] as String;
      final newRefreshToken = response.data['refresh_token'] as String;
      await _storage.saveTokens(accessToken: accessToken, refreshToken: newRefreshToken);
      return accessToken;
    } catch (_) {
      await _storage.clear();
      return null;
    }
  }

  static ApiException mapError(DioException error) {
    final data = error.response?.data;
    String message = 'Une erreur réseau est survenue';
    if (data is Map && data['detail'] != null) {
      message = data['detail'].toString();
    } else if (error.type == DioExceptionType.connectionTimeout ||
        error.type == DioExceptionType.connectionError) {
      message = 'Impossible de contacter le serveur CyberPulse';
    }
    return ApiException(message, statusCode: error.response?.statusCode);
  }
}
