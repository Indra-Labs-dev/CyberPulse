import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/watchlist.dart';
import '../data/watchlist_service.dart';

final watchlistServiceProvider = Provider<WatchlistService>((ref) {
  return WatchlistService(ref.watch(dioClientProvider));
});

final watchlistControllerProvider =
    StateNotifierProvider<WatchlistController, AsyncValue<List<WatchlistEntry>>>((ref) {
  return WatchlistController(ref.watch(watchlistServiceProvider));
});

class WatchlistController extends StateNotifier<AsyncValue<List<WatchlistEntry>>> {
  WatchlistController(this._service) : super(const AsyncValue.loading()) {
    refresh();
  }

  final WatchlistService _service;

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _service.list());
  }

  Future<void> add({required String productName, String? vendor, String alertThreshold = 'MEDIUM'}) async {
    await _service.create(productName: productName, vendor: vendor, alertThreshold: alertThreshold);
    await refresh();
  }

  Future<void> remove(int id) async {
    await _service.delete(id);
    await refresh();
  }
}
