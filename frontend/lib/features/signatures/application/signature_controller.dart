import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/signature.dart';
import '../data/signature_service.dart';

final signatureServiceProvider = Provider<SignatureService>((ref) {
  return SignatureService(ref.watch(dioClientProvider));
});

final signatureControllerProvider =
    StateNotifierProvider<SignatureController, AsyncValue<List<SignatureRule>>>((ref) {
  return SignatureController(ref.watch(signatureServiceProvider));
});

class SignatureController extends StateNotifier<AsyncValue<List<SignatureRule>>> {
  SignatureController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final SignatureService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> generateYara({required String name, String? description, required List<String> strings, required List<String> hashes}) async {
    await _service.generateYara(name: name, description: description, strings: strings, hashes: hashes);
    await refresh();
  }

  Future<void> generateSigma({
    required String name,
    String? description,
    required Map<String, dynamic> logSource,
    required Map<String, dynamic> detectionSelection,
    required String level,
  }) async {
    await _service.generateSigma(
      name: name,
      description: description,
      logSource: logSource,
      detectionSelection: detectionSelection,
      level: level,
    );
    await refresh();
  }

  Future<void> delete(int id) async {
    await _service.delete(id);
    await refresh();
  }
}
