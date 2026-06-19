import 'package:dio/dio.dart';

import '../../../core/network/dio_client.dart';
import '../../../models/productivity.dart';

class ProductivityService {
  ProductivityService(this._dioClient);

  final DioClient _dioClient;

  Dio get _dio => _dioClient.dio;

  Future<List<QuickNote>> listNotes() async {
    try {
      final response = await _dio.get('/productivity/notes');
      return (response.data as List<dynamic>).map((e) => QuickNote.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<QuickNote> createNote(String content) async {
    try {
      final response = await _dio.post('/productivity/notes', data: {'content': content});
      return QuickNote.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> deleteNote(int id) async {
    try {
      await _dio.delete('/productivity/notes/$id');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<List<TaskItem>> listTasks() async {
    try {
      final response = await _dio.get('/productivity/tasks');
      return (response.data as List<dynamic>).map((e) => TaskItem.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<TaskItem> createTask({required String title, String priority = 'MEDIUM'}) async {
    try {
      final response = await _dio.post('/productivity/tasks', data: {'title': title, 'priority': priority});
      return TaskItem.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<TaskItem> updateTaskStatus(int id, String status) async {
    try {
      final response = await _dio.patch('/productivity/tasks/$id', data: {'status': status});
      return TaskItem.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }

  Future<void> deleteTask(int id) async {
    try {
      await _dio.delete('/productivity/tasks/$id');
    } on DioException catch (e) {
      throw DioClient.mapError(e);
    }
  }
}
