import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/correlation.dart';

class CorrelationService {
  CorrelationService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<ThreatActor>> listActors() async {
    try {
      final response = await _dio.get('/correlation/actors');
      return (response.data as List<dynamic>)
          .map((e) => ThreatActor.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<Campaign>> listCampaigns() async {
    try {
      final response = await _dio.get('/correlation/campaigns');
      return (response.data as List<dynamic>).map((e) => Campaign.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<CampaignDetail> getCampaign(int id) async {
    try {
      final response = await _dio.get('/correlation/campaigns/$id');
      return CampaignDetail.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<CorrelationGraph> getGraph(int id) async {
    try {
      final response = await _dio.get('/correlation/campaigns/$id/graph');
      return CorrelationGraph.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<TimelineEvent>> getTimeline(int id) async {
    try {
      final response = await _dio.get('/correlation/campaigns/$id/timeline');
      return (response.data as List<dynamic>)
          .map((e) => TimelineEvent.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<Campaign>> detect() async {
    try {
      final response = await _dio.post('/correlation/detect');
      return (response.data as List<dynamic>).map((e) => Campaign.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
