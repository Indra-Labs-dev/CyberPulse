import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/vuln_scan.dart';
import '../data/scanner_service.dart';

final scannerServiceProvider = Provider<ScannerService>((ref) {
  return ScannerService(ref.watch(dioClientProvider));
});

final scannerControllerProvider =
    StateNotifierProvider<ScannerController, AsyncValue<List<VulnScan>>>((ref) {
  return ScannerController(ref.watch(scannerServiceProvider));
});

class ScannerController extends StateNotifier<AsyncValue<List<VulnScan>>> {
  ScannerController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final ScannerService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> runPortScan({required String target, List<int>? ports, int? scheduleMinutes}) async {
    await _service.portScan(target: target, ports: ports, scheduleMinutes: scheduleMinutes);
    await refresh();
  }

  Future<void> runFileScan({required String filename, required String content}) async {
    await _service.fileScan(filename: filename, content: content);
    await refresh();
  }
}
