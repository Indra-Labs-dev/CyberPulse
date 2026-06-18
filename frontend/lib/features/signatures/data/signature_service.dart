import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/signature.dart';

class SignatureService {
  SignatureService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<SignatureRule>> list({String? type}) async {
    try {
      final response = await _dio.get('/signatures', queryParameters: {'type': ?type});
      return (response.data as List<dynamic>)
          .map((e) => SignatureRule.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<SignatureRule> generateYara({
    required String name,
    String? description,
    List<String> strings = const [],
    List<String> hashes = const [],
  }) async {
    try {
      final response = await _dio.post('/signatures/generate/yara', data: {
        'name': name,
        'description': ?description,
        'strings': strings,
        'hashes': hashes,
      });
      return SignatureRule.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<SignatureRule> generateSigma({
    required String name,
    String? description,
    Map<String, dynamic> logSource = const {},
    Map<String, dynamic> detectionSelection = const {},
    String level = 'medium',
  }) async {
    try {
      final response = await _dio.post('/signatures/generate/sigma', data: {
        'name': name,
        'description': ?description,
        'log_source': logSource,
        'detection_selection': detectionSelection,
        'level': level,
      });
      return SignatureRule.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> delete(int id) async {
    try {
      await _dio.delete('/signatures/$id');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<String> download(SignatureRule signature) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final extension = signature.type == 'YARA' ? 'yar' : 'yml';
      final localPath = '${dir.path}/${signature.name}_${signature.id}.$extension';
      await _dio.download('/signatures/${signature.id}/export', localPath);
      return localPath;
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
