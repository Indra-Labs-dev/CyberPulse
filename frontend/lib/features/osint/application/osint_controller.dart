import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/osint.dart';
import '../data/osint_service.dart';

final osintServiceProvider = Provider<OsintService>((ref) {
  return OsintService(ref.watch(dioClientProvider));
});

final osintControllerProvider =
    StateNotifierProvider<OsintController, AsyncValue<List<OsintResult>>>((ref) {
  return OsintController(ref.watch(osintServiceProvider));
});

class OsintController extends StateNotifier<AsyncValue<List<OsintResult>>> {
  OsintController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final OsintService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> lookup({required String type, required String target}) async {
    await _service.lookup(type: type, target: target);
    await refresh();
  }
}
