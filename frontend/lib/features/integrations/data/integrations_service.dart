import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/integration.dart';

class IntegrationsService {
  IntegrationsService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<ApiKeySummary>> listApiKeys() async {
    try {
      final response = await _dio.get('/api-keys');
      return (response.data as List<dynamic>).map((e) => ApiKeySummary.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  /// Returns the raw secret — only ever available at creation time.
  Future<String> createApiKey({required String name, int rateLimitPerMinute = 60}) async {
    try {
      final response = await _dio.post('/api-keys', data: {
        'name': name,
        'rate_limit_per_minute': rateLimitPerMinute,
      });
      return response.data['api_key'] as String;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> revokeApiKey(int id) async {
    try {
      await _dio.post('/api-keys/$id/revoke');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<WebhookSubscription>> listWebhooks() async {
    try {
      final response = await _dio.get('/webhooks');
      return (response.data as List<dynamic>)
          .map((e) => WebhookSubscription.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<WebhookSubscription> createWebhook({
    required String platform,
    required String url,
    List<String> events = const ['*'],
  }) async {
    try {
      final response = await _dio.post('/webhooks', data: {
        'platform': platform,
        'url': url,
        'events': events,
      });
      return WebhookSubscription.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> deleteWebhook(int id) async {
    try {
      await _dio.delete('/webhooks/$id');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
