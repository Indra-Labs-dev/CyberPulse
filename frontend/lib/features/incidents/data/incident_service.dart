import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/incident.dart';

class IncidentService {
  IncidentService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<Incident>> list({String? status}) async {
    try {
      final response = await _dio.get('/incidents', queryParameters: {'status': ?status});
      return (response.data as List<dynamic>)
          .map((e) => Incident.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Incident> getById(int id) async {
    try {
      final response = await _dio.get('/incidents/$id');
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Incident> create({
    required String title,
    String? description,
    String severity = 'MEDIUM',
    int? cveId,
  }) async {
    try {
      final response = await _dio.post('/incidents', data: {
        'title': title,
        'description': ?description,
        'severity': severity,
        'cve_id': ?cveId,
      });
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Incident> updateStatus(int id, {required String status, String? resolutionNotes}) async {
    try {
      final response = await _dio.post('/incidents/$id/status', data: {
        'status': status,
        'resolution_notes': ?resolutionNotes,
      });
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Incident> assign(int id, int assigneeId) async {
    try {
      final response = await _dio.post('/incidents/$id/assign/$assigneeId');
      return Incident.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<IncidentActivity>> activity(int id) async {
    try {
      final response = await _dio.get('/incidents/$id/activity');
      return (response.data as List<dynamic>)
          .map((e) => IncidentActivity.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<IncidentMetrics> metrics() async {
    try {
      final response = await _dio.get('/incidents/metrics');
      return IncidentMetrics.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
