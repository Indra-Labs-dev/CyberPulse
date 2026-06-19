import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/integration.dart';
import '../data/integrations_service.dart';

final integrationsServiceProvider = Provider<IntegrationsService>((ref) {
  return IntegrationsService(ref.watch(dioClientProvider));
});

final apiKeysProvider =
    StateNotifierProvider<ApiKeysController, AsyncValue<List<ApiKeySummary>>>((ref) {
  return ApiKeysController(ref.watch(integrationsServiceProvider));
});

class ApiKeysController extends StateNotifier<AsyncValue<List<ApiKeySummary>>> {
  ApiKeysController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final IntegrationsService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.listApiKeys());
  }

  Future<String> create(String name) async {
    final key = await _service.createApiKey(name: name);
    await refresh();
    return key;
  }

  Future<void> revoke(int id) async {
    await _service.revokeApiKey(id);
    await refresh();
  }
}

final webhooksProvider =
    StateNotifierProvider<WebhooksController, AsyncValue<List<WebhookSubscription>>>((ref) {
  return WebhooksController(ref.watch(integrationsServiceProvider));
});

class WebhooksController extends StateNotifier<AsyncValue<List<WebhookSubscription>>> {
  WebhooksController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final IntegrationsService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.listWebhooks());
  }

  Future<void> create({required String platform, required String url}) async {
    await _service.createWebhook(platform: platform, url: url);
    await refresh();
  }

  Future<void> delete(int id) async {
    await _service.deleteWebhook(id);
    await refresh();
  }
}
