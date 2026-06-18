import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/cve.dart';

class CveService {
  CveService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<Cve>> list({CveFilters filters = const CveFilters(), int page = 1, int pageSize = 20}) async {
    try {
      final response = await _dio.get('/cves', queryParameters: {
        ...filters.toQueryParams(),
        'page': page,
        'page_size': pageSize,
      });
      return (response.data as List<dynamic>)
          .map((e) => Cve.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Cve> getById(int id) async {
    try {
      final response = await _dio.get('/cves/$id');
      return Cve.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<Cve>> sync({int count = 5}) async {
    try {
      final response = await _dio.post('/cves/sync', queryParameters: {'count': count});
      return (response.data as List<dynamic>)
          .map((e) => Cve.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
