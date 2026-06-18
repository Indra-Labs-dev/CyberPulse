import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/osint.dart';

class OsintService {
  OsintService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<OsintResult>> list({String? type}) async {
    try {
      final response = await _dio.get('/osint', queryParameters: {'type': ?type});
      return (response.data as List<dynamic>)
          .map((e) => OsintResult.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<OsintResult> lookup({required String type, required String target}) async {
    try {
      final response = await _dio.post('/osint/lookup', data: {'type': type, 'target': target});
      return OsintResult.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
