import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/stats.dart';

class StatsService {
  StatsService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<PersonalStats> personal() async {
    try {
      final response = await _dio.get('/stats/personal');
      return PersonalStats.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<TeamStats> team() async {
    try {
      final response = await _dio.get('/stats/team');
      return TeamStats.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<TrendPoint>> trends({int days = 30}) async {
    try {
      final response = await _dio.get('/stats/trends', queryParameters: {'days': days});
      return (response.data as List<dynamic>).map((e) => TrendPoint.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
