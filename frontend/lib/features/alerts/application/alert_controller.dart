import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/notifications/app_messenger.dart';
import '../../../core/notifications/notification_service.dart';
import '../../../core/providers/core_providers.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/alert.dart';
import '../data/alert_service.dart';

final alertServiceProvider = Provider<AlertService>((ref) {
  return AlertService(ref.watch(dioClientProvider));
});

final alertControllerProvider =
    StateNotifierProvider<AlertController, AsyncValue<List<CyberAlert>>>((ref) {
  final controller = AlertController(ref.watch(alertServiceProvider));
  final socket = ref.watch(webSocketServiceProvider);
  final subscription = socket.onAlert.listen(controller.handleRealtimeAlert);
  ref.onDispose(subscription.cancel);
  return controller;
});

/// Count of unacknowledged alerts, used for the navigation badge.
final unacknowledgedAlertCountProvider = Provider<int>((ref) {
  final alerts = ref.watch(alertControllerProvider).valueOrNull ?? [];
  return alerts.where((a) => a.status == 'NEW').length;
});

class AlertController extends StateNotifier<AsyncValue<List<CyberAlert>>> {
  AlertController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final AlertService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> acknowledge(int id) async {
    final updated = await _service.acknowledge(id);
    state = state.whenData((alerts) =>
        alerts.map((a) => a.id == updated.id ? updated : a).toList());
  }

  void handleRealtimeAlert(Map<String, dynamic> payload) {
    final incoming = CyberAlert(
      id: payload['id'] as int? ?? DateTime.now().millisecondsSinceEpoch,
      cveId: payload['cve_id'] as int?,
      userId: payload['user_id'] as int? ?? 0,
      type: payload['type'] as String? ?? 'SYSTEM',
      status: 'NEW',
      severity: payload['severity'] as String? ?? 'MEDIUM',
      message: payload['message'] as String? ?? 'Nouvelle alerte CyberPulse',
      createdAt: DateTime.now(),
    );

    state = state.whenData((alerts) => [incoming, ...alerts]);

    NotificationService.instance.showAlert(
      title: 'Alerte ${incoming.severity}',
      body: incoming.message,
    );
    showAppToast(
      title: 'Alerte ${incoming.severity}',
      body: incoming.message,
      accent: AppColors.severityColor(incoming.severity),
    );
  }
}
