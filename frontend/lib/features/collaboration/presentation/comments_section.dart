import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../application/collaboration_providers.dart';

/// Embeddable comment thread with @mention support, used on CVE/article/
/// incident detail screens.
class CommentsSection extends ConsumerStatefulWidget {
  const CommentsSection({super.key, required this.entityType, required this.entityId});

  final String entityType;
  final int entityId;

  @override
  ConsumerState<CommentsSection> createState() => _CommentsSectionState();
}

class _CommentsSectionState extends ConsumerState<CommentsSection> {
  final _controller = TextEditingController();
  bool _isSending = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  ({String entityType, int entityId}) get _params =>
      (entityType: widget.entityType, entityId: widget.entityId);

  Future<void> _send() async {
    if (_controller.text.trim().isEmpty) return;
    setState(() => _isSending = true);
    try {
      await ref.read(collaborationServiceProvider).addComment(
            entityType: widget.entityType,
            entityId: widget.entityId,
            content: _controller.text.trim(),
          );
      _controller.clear();
      ref.invalidate(commentsProvider(_params));
    } finally {
      if (mounted) setState(() => _isSending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final commentsAsync = ref.watch(commentsProvider(_params));
    final dateFormat = DateFormat('dd/MM HH:mm');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Commentaires', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 12),
        commentsAsync.when(
          data: (comments) {
            if (comments.isEmpty) {
              return const Text('Aucun commentaire. Démarrez la discussion.',
                  style: TextStyle(color: AppColors.textSecondary));
            }
            return Column(
              children: comments.map((comment) {
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(comment.content),
                        const SizedBox(height: 6),
                        Text(
                          'Utilisateur #${comment.userId} • ${dateFormat.format(comment.createdAt)}',
                          style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                );
              }).toList(),
            );
          },
          error: (_, _) => const Text('Erreur de chargement des commentaires'),
          loading: () => const Center(child: CircularProgressIndicator()),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _controller,
                decoration: const InputDecoration(
                  hintText: 'Ajouter un commentaire... (utilisez @nom pour mentionner)',
                ),
                onSubmitted: (_) => _send(),
              ),
            ),
            const SizedBox(width: 8),
            IconButton(
              icon: _isSending
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.send, color: AppColors.neonBlue),
              onPressed: _isSending ? null : _send,
            ),
          ],
        ),
      ],
    );
  }
}
