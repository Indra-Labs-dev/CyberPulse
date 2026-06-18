import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/playbook.dart';

class PlaybookService {
  PlaybookService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<Playbook>> list() async {
    try {
      final response = await _dio.get('/playbooks');
      return (response.data as List<dynamic>).map((e) => Playbook.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<PlaybookTemplate>> templates() async {
    try {
      final response = await _dio.get('/playbooks/templates');
      return (response.data as List<dynamic>)
          .map((e) => PlaybookTemplate.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<Playbook> create({
    required String name,
    String? description,
    required String triggerType,
    Map<String, dynamic> triggerConfig = const {},
    required List<PlaybookAction> actions,
  }) async {
    try {
      final response = await _dio.post('/playbooks', data: {
        'name': name,
        'description': ?description,
        'trigger_type': triggerType,
        'trigger_config': triggerConfig,
        'actions': actions.map((a) => a.toJson()).toList(),
      });
      return Playbook.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> delete(int id) async {
    try {
      await _dio.delete('/playbooks/$id');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<PlaybookRun> run(int id) async {
    try {
      final response = await _dio.post('/playbooks/$id/run');
      return PlaybookRun.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<PlaybookRun>> runs(int id) async {
    try {
      final response = await _dio.get('/playbooks/$id/runs');
      return (response.data as List<dynamic>).map((e) => PlaybookRun.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
