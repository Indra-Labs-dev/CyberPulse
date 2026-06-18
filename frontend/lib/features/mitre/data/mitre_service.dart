import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/mitre.dart';

class MitreService {
  MitreService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<AttackMatrix> getMatrix() async {
    try {
      final response = await _dio.get('/mitre/matrix');
      return AttackMatrix.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<HeatmapEntry>> getHeatmap() async {
    try {
      final response = await _dio.get('/mitre/heatmap');
      return (response.data as List<dynamic>)
          .map((e) => HeatmapEntry.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> mapCve(int cveId) async {
    try {
      await _dio.post('/mitre/map/$cveId');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
