import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/collaboration.dart';

class CollaborationService {
  CollaborationService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<CyberComment>> listComments({required String entityType, required int entityId}) async {
    try {
      final response = await _dio.get('/collaboration/comments', queryParameters: {
        'entity_type': entityType,
        'entity_id': entityId,
      });
      return (response.data as List<dynamic>).map((e) => CyberComment.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<CyberComment> addComment({required String entityType, required int entityId, required String content}) async {
    try {
      final response = await _dio.post('/collaboration/comments', data: {
        'entity_type': entityType,
        'entity_id': entityId,
        'content': content,
      });
      return CyberComment.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<SavedSearch>> listSearches() async {
    try {
      final response = await _dio.get('/collaboration/searches');
      return (response.data as List<dynamic>).map((e) => SavedSearch.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<SavedSearch> saveSearch({
    required String name,
    required String entityType,
    required Map<String, dynamic> filters,
    bool isShared = false,
  }) async {
    try {
      final response = await _dio.post('/collaboration/searches', data: {
        'name': name,
        'entity_type': entityType,
        'filters': filters,
        'is_shared': isShared,
      });
      return SavedSearch.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<ActivityLogEntry>> listActivity({int limit = 50}) async {
    try {
      final response = await _dio.get('/collaboration/activity', queryParameters: {'limit': limit});
      return (response.data as List<dynamic>)
          .map((e) => ActivityLogEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
