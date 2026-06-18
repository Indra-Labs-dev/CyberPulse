import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../core/providers/core_providers.dart';
import '../../../core/theme/app_colors.dart';
import '../../../models/article.dart';
import '../data/article_service.dart';

final _articleDetailProvider =
    FutureProvider.autoDispose.family<ScrapedArticle, int>((ref, id) async {
  final service = ArticleService(ref.watch(dioClientProvider));
  return service.getById(id);
});

class ArticleReaderScreen extends ConsumerWidget {
  const ArticleReaderScreen({super.key, required this.articleId});

  final int articleId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final articleAsync = ref.watch(_articleDetailProvider(articleId));

    return Scaffold(
      appBar: AppBar(title: const Text('Mode lecture')),
      body: articleAsync.when(
        data: (article) => Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 760),
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(32),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Wrap(
                    spacing: 8,
                    children: [
                      Chip(label: Text(article.source), backgroundColor: AppColors.panelBlackAlt),
                      if (article.category != null)
                        Chip(
                          label: Text(article.category!),
                          backgroundColor: AppColors.neonBlue.withValues(alpha: 0.15),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(article.title, style: Theme.of(context).textTheme.headlineSmall),
                  const SizedBox(height: 8),
                  Text(
                    [
                      if (article.author != null) article.author,
                      '${article.readTime ?? 1} min de lecture',
                    ].join(' • '),
                    style: const TextStyle(color: AppColors.textSecondary),
                  ),
                  const Divider(height: 32, color: AppColors.borderColor),
                  MarkdownBody(
                    data: article.content ?? article.summary ?? 'Contenu indisponible.',
                    styleSheet: MarkdownStyleSheet(
                      p: const TextStyle(color: AppColors.textPrimary, height: 1.6, fontSize: 15),
                      h1: const TextStyle(color: AppColors.neonBlue),
                      h2: const TextStyle(color: AppColors.neonBlue),
                      a: const TextStyle(color: AppColors.neonBlue),
                    ),
                  ),
                  if (article.mentionedCves.isNotEmpty) ...[
                    const SizedBox(height: 24),
                    Text('CVE mentionnées', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: article.mentionedCves
                          .map((c) => Chip(label: Text(c), backgroundColor: AppColors.alertRedDim))
                          .toList(),
                    ),
                  ],
                  if (article.sourceUrl != null) ...[
                    const SizedBox(height: 24),
                    OutlinedButton.icon(
                      onPressed: () => launchUrl(Uri.parse(article.sourceUrl!)),
                      icon: const Icon(Icons.open_in_new, size: 16),
                      label: const Text('Voir la source originale'),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}
