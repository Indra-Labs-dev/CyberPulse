import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

import '../../../core/network/dio_client.dart';

class ImportExportService {
  ImportExportService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<Map<String, dynamic>> importCvesJson(String filename, List<int> bytes) async {
    try {
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: filename),
      });
      final response = await _dio.post('/import-export/import/cves/json', data: formData);
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Map<String, dynamic>> importCvesCsv(String filename, List<int> bytes) async {
    try {
      final formData = FormData.fromMap({
        'file': MultipartFile.fromBytes(bytes, filename: filename),
      });
      final response = await _dio.post('/import-export/import/cves/csv', data: formData);
      return response.data as Map<String, dynamic>;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<String> exportCves(String format) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final extension = format == 'csv' ? 'csv' : (format == 'xml' || format == 'openioc') ? 'xml' : 'json';
      final localPath = '${dir.path}/cyberpulse_cves_$format.$extension';
      await _dio.download('/import-export/export/cves', localPath, queryParameters: {'format': format});
      return localPath;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<String> backup() async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final localPath = '${dir.path}/cyberpulse_backup_${DateTime.now().millisecondsSinceEpoch}.json';
      await _dio.download('/import-export/backup', localPath);
      return localPath;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
