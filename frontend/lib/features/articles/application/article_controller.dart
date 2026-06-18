import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/article.dart';
import '../data/article_service.dart';

final articleServiceProvider = Provider<ArticleService>((ref) {
  return ArticleService(ref.watch(dioClientProvider));
});

final articleSearchProvider = StateProvider<String>((ref) => '');
final articleCategoryFilterProvider = StateProvider<String?>((ref) => null);

final articleControllerProvider =
    StateNotifierProvider<ArticleController, AsyncValue<List<ScrapedArticle>>>((ref) {
  final controller = ArticleController(ref);
  final socket = ref.watch(webSocketServiceProvider);
  final subscription = socket.onNewArticle.listen((_) => controller.refresh());
  ref.onDispose(subscription.cancel);
  return controller;
});

class ArticleController extends StateNotifier<AsyncValue<List<ScrapedArticle>>> {
  ArticleController(this._ref) : super(const AsyncValue.loading()) {
    refresh();
  }

  final Ref _ref;
  ArticleService get _service => _ref.read(articleServiceProvider);

  Future<void> refresh() async {
    state = const AsyncValue.loading();
    final search = _ref.read(articleSearchProvider);
    final category = _ref.read(articleCategoryFilterProvider);
    state = await AsyncValue.guard(
      () => _service.list(search: search.isEmpty ? null : search, category: category, pageSize: 50),
    );
  }

  Future<void> toggleFavorite(int id) async {
    final updated = await _service.toggleFavorite(id);
    state = state.whenData((articles) => articles.map((a) => a.id == id ? updated : a).toList());
  }

  Future<void> markRead(int id) async {
    final updated = await _service.markRead(id);
    state = state.whenData((articles) => articles.map((a) => a.id == id ? updated : a).toList());
  }

  Future<void> triggerScrape() async {
    await _service.triggerScrape();
    await refresh();
  }
}
