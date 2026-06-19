import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/productivity.dart';
import '../data/productivity_service.dart';

final productivityServiceProvider = Provider<ProductivityService>((ref) {
  return ProductivityService(ref.watch(dioClientProvider));
});

final notesControllerProvider =
    StateNotifierProvider<NotesController, AsyncValue<List<QuickNote>>>((ref) {
  return NotesController(ref.watch(productivityServiceProvider));
});

class NotesController extends StateNotifier<AsyncValue<List<QuickNote>>> {
  NotesController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final ProductivityService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.listNotes());
  }

  Future<void> add(String content) async {
    await _service.createNote(content);
    await refresh();
  }

  Future<void> delete(int id) async {
    await _service.deleteNote(id);
    await refresh();
  }
}

final tasksControllerProvider =
    StateNotifierProvider<TasksController, AsyncValue<List<TaskItem>>>((ref) {
  return TasksController(ref.watch(productivityServiceProvider));
});

class TasksController extends StateNotifier<AsyncValue<List<TaskItem>>> {
  TasksController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final ProductivityService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.listTasks());
  }

  Future<void> add(String title, {String priority = 'MEDIUM'}) async {
    await _service.createTask(title: title, priority: priority);
    await refresh();
  }

  Future<void> setStatus(int id, String status) async {
    await _service.updateTaskStatus(id, status);
    await refresh();
  }

  Future<void> delete(int id) async {
    await _service.deleteTask(id);
    await refresh();
  }
}
