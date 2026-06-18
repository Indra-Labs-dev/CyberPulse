import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/incident.dart';
import '../data/incident_service.dart';

final incidentServiceProvider = Provider<IncidentService>((ref) {
  return IncidentService(ref.watch(dioClientProvider));
});

final incidentControllerProvider =
    StateNotifierProvider<IncidentController, AsyncValue<List<Incident>>>((ref) {
  return IncidentController(ref.watch(incidentServiceProvider));
});

final incidentMetricsProvider = FutureProvider.autoDispose<IncidentMetrics>((ref) {
  return ref.watch(incidentServiceProvider).metrics();
});

final incidentDetailProvider = FutureProvider.autoDispose.family<Incident, int>((ref, id) {
  return ref.watch(incidentServiceProvider).getById(id);
});

final incidentActivityProvider = FutureProvider.autoDispose.family<List<IncidentActivity>, int>((ref, id) {
  return ref.watch(incidentServiceProvider).activity(id);
});

class IncidentController extends StateNotifier<AsyncValue<List<Incident>>> {
  IncidentController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final IncidentService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> create({required String title, String? description, String severity = 'MEDIUM', int? cveId}) async {
    await _service.create(title: title, description: description, severity: severity, cveId: cveId);
    await refresh();
  }

  Future<void> updateStatus(int id, String status, {String? resolutionNotes}) async {
    await _service.updateStatus(id, status: status, resolutionNotes: resolutionNotes);
    await refresh();
  }

  Future<void> assign(int id, int assigneeId) async {
    await _service.assign(id, assigneeId);
    await refresh();
  }
}
