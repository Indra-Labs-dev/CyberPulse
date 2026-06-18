import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/vuln_scan.dart';

class ScannerService {
  ScannerService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<VulnScan>> list() async {
    try {
      final response = await _dio.get('/scanner');
      return (response.data as List<dynamic>).map((e) => VulnScan.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<VulnScan> portScan({required String target, List<int>? ports, int? scheduleMinutes}) async {
    try {
      final response = await _dio.post('/scanner/port-scan', data: {
        'target': target,
        'ports': ports,
        'schedule_minutes': ?scheduleMinutes,
      });
      return VulnScan.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<VulnScan> fileScan({required String filename, required String content}) async {
    try {
      final formData = FormData.fromMap({
        'file': MultipartFile.fromString(content, filename: filename),
      });
      final response = await _dio.post('/scanner/file-scan', data: formData);
      return VulnScan.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
