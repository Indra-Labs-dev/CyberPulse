import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/article.dart';

class ArticleService {
  ArticleService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<ScrapedArticle>> list({
    String? source,
    String? category,
    String? search,
    bool? isFavorite,
    int page = 1,
    int pageSize = 20,
  }) async {
    try {
      final response = await _dio.get('/articles', queryParameters: {
        'source': ?source,
        'category': ?category,
        if (search != null && search.isNotEmpty) 'search': search,
        'is_favorite': ?isFavorite,
        'page': page,
        'page_size': pageSize,
      });
      return (response.data as List<dynamic>)
          .map((e) => ScrapedArticle.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<ScrapedArticle> getById(int id) async {
    try {
      final response = await _dio.get('/articles/$id');
      return ScrapedArticle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<ScrapedArticle> toggleFavorite(int id) async {
    try {
      final response = await _dio.post('/articles/$id/favorite');
      return ScrapedArticle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<ScrapedArticle> markRead(int id) async {
    try {
      final response = await _dio.post('/articles/$id/read');
      return ScrapedArticle.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<ScrapedArticle>> triggerScrape() async {
    try {
      final response = await _dio.post('/articles/scrape');
      return (response.data as List<dynamic>)
          .map((e) => ScrapedArticle.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
