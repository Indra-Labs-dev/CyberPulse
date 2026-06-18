import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/watchlist.dart';

class WatchlistService {
  WatchlistService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<WatchlistEntry>> list() async {
    try {
      final response = await _dio.get('/watchlists');
      return (response.data as List<dynamic>)
          .map((e) => WatchlistEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<WatchlistEntry> create({
    required String productName,
    String? vendor,
    String? versionPattern,
    String alertThreshold = 'MEDIUM',
  }) async {
    try {
      final response = await _dio.post('/watchlists', data: {
        'product_name': productName,
        'vendor': ?vendor,
        'version_pattern': ?versionPattern,
        'alert_threshold': alertThreshold,
      });
      return WatchlistEntry.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> delete(int id) async {
    try {
      await _dio.delete('/watchlists/$id');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
