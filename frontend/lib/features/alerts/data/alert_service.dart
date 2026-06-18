import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/alert.dart';

class AlertService {
  AlertService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<CyberAlert>> list({String? status}) async {
    try {
      final response = await _dio.get('/alerts', queryParameters: {
        'status': ?status,
      });
      return (response.data as List<dynamic>)
          .map((e) => CyberAlert.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<CyberAlert> acknowledge(int id) async {
    try {
      final response = await _dio.post('/alerts/$id/acknowledge');
      return CyberAlert.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
