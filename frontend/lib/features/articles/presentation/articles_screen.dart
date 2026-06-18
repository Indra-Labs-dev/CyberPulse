import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/article.dart';
import '../application/article_controller.dart';

class ArticlesScreen extends ConsumerStatefulWidget {
  const ArticlesScreen({super.key});

  @override
  ConsumerState<ArticlesScreen> createState() => _ArticlesScreenState();
}

class _ArticlesScreenState extends ConsumerState<ArticlesScreen> {
  final _searchController = TextEditingController();
  bool _isScraping = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _triggerScrape() async {
    setState(() => _isScraping = true);
    try {
      await ref.read(articleControllerProvider.notifier).triggerScrape();
    } finally {
      if (mounted) setState(() => _isScraping = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final articlesAsync = ref.watch(articleControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Articles & Blogs'),
        actions: [
          IconButton(
            tooltip: 'Lancer le scraping',
            icon: _isScraping
                ? const SizedBox(
                    width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.travel_explore_outlined),
            onPressed: _isScraping ? null : _triggerScrape,
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                labelText: 'Rechercher un article',
                prefixIcon: Icon(Icons.search),
              ),
              onSubmitted: (value) {
                ref.read(articleSearchProvider.notifier).state = value;
                ref.read(articleControllerProvider.notifier).refresh();
              },
            ),
          ),
          const Divider(height: 1, color: AppColors.borderColor),
          Expanded(
            child: articlesAsync.when(
              data: (articles) {
                if (articles.isEmpty) {
                  return const Center(
                    child: Text('Aucun article. Lancez une session de scraping.'),
                  );
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: articles.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) =>
                      _ArticleRow(article: articles[index]),
                );
              },
              error: (e, _) => Center(child: Text('Erreur: $e')),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ),
        ],
      ),
    );
  }
}

class _ArticleRow extends ConsumerWidget {
  const _ArticleRow({required this.article});

  final ScrapedArticle article;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () {
          ref.read(articleControllerProvider.notifier).markRead(article.id);
          context.push('/articles/${article.id}');
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        if (!article.isRead)
                          Container(
                            width: 8,
                            height: 8,
                            margin: const EdgeInsets.only(right: 8),
                            decoration: const BoxDecoration(
                                color: AppColors.neonBlue, shape: BoxShape.circle),
                          ),
                        Expanded(
                          child: Text(article.title,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontWeight: FontWeight.w600)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      '${article.source} • ${article.category ?? 'Actualités'} • ${article.readTime ?? 1} min',
                      style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: Icon(
                  article.isFavorite ? Icons.star : Icons.star_border,
                  color: article.isFavorite ? AppColors.warningAmber : AppColors.textSecondary,
                ),
                onPressed: () =>
                    ref.read(articleControllerProvider.notifier).toggleFavorite(article.id),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
