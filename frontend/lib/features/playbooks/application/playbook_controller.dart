import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/playbook.dart';
import '../data/playbook_service.dart';

final playbookServiceProvider = Provider<PlaybookService>((ref) {
  return PlaybookService(ref.watch(dioClientProvider));
});

final playbookTemplatesProvider = FutureProvider.autoDispose<List<PlaybookTemplate>>((ref) {
  return ref.watch(playbookServiceProvider).templates();
});

final playbookRunsProvider = FutureProvider.autoDispose.family<List<PlaybookRun>, int>((ref, id) {
  return ref.watch(playbookServiceProvider).runs(id);
});

final playbookControllerProvider =
    StateNotifierProvider<PlaybookController, AsyncValue<List<Playbook>>>((ref) {
  return PlaybookController(ref.watch(playbookServiceProvider));
});

class PlaybookController extends StateNotifier<AsyncValue<List<Playbook>>> {
  PlaybookController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final PlaybookService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> createFromTemplate(PlaybookTemplate template) async {
    await _service.create(
      name: template.name,
      description: template.description,
      triggerType: template.triggerType,
      triggerConfig: template.triggerConfig,
      actions: template.actions,
    );
    await refresh();
  }

  Future<void> create({
    required String name,
    String? description,
    required String triggerType,
    required List<PlaybookAction> actions,
  }) async {
    await _service.create(name: name, description: description, triggerType: triggerType, actions: actions);
    await refresh();
  }

  Future<void> delete(int id) async {
    await _service.delete(id);
    await refresh();
  }

  Future<void> run(int id) async {
    await _service.run(id);
  }
}
