import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/playbook.dart';
import '../application/playbook_controller.dart';

class PlaybooksScreen extends ConsumerWidget {
  const PlaybooksScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final playbooksAsync = ref.watch(playbookControllerProvider);
    final templatesAsync = ref.watch(playbookTemplatesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Playbooks Automatisés'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(playbookControllerProvider.notifier).refresh(),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Templates pré-configurés', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            templatesAsync.when(
              data: (templates) => Wrap(
                spacing: 12,
                runSpacing: 12,
                children: templates.map((template) {
                  return SizedBox(
                    width: 280,
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(template.name, style: const TextStyle(fontWeight: FontWeight.bold)),
                            const SizedBox(height: 6),
                            Text(
                              template.description,
                              style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                              maxLines: 3,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 10),
                            Align(
                              alignment: Alignment.centerRight,
                              child: TextButton(
                                onPressed: () => ref
                                    .read(playbookControllerProvider.notifier)
                                    .createFromTemplate(template),
                                child: const Text('Utiliser ce modèle'),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
              error: (_, _) => const Text('Erreur de chargement des modèles'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
            const SizedBox(height: 24),
            Text('Mes playbooks', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            playbooksAsync.when(
              data: (playbooks) {
                if (playbooks.isEmpty) {
                  return const Text('Aucun playbook configuré. Utilisez un modèle ci-dessus.');
                }
                return Column(
                  children: playbooks.map((playbook) => _PlaybookCard(playbook: playbook)).toList(),
                );
              },
              error: (e, _) => Text('Erreur: $e'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}

class _PlaybookCard extends ConsumerStatefulWidget {
  const _PlaybookCard({required this.playbook});

  final Playbook playbook;

  @override
  ConsumerState<_PlaybookCard> createState() => _PlaybookCardState();
}

class _PlaybookCardState extends ConsumerState<_PlaybookCard> {
  bool _isRunning = false;

  Future<void> _run() async {
    setState(() => _isRunning = true);
    try {
      await ref.read(playbookControllerProvider.notifier).run(widget.playbook.id);
      ref.invalidate(playbookRunsProvider(widget.playbook.id));
    } finally {
      if (mounted) setState(() => _isRunning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final runsAsync = ref.watch(playbookRunsProvider(widget.playbook.id));
    final dateFormat = DateFormat('dd/MM HH:mm');

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ExpansionTile(
        leading: Icon(
          widget.playbook.isActive ? Icons.play_circle_outline : Icons.pause_circle_outline,
          color: widget.playbook.isActive ? AppColors.securityGreen : AppColors.textSecondary,
        ),
        title: Text(widget.playbook.name),
        subtitle: Text(
          'Déclencheur: ${widget.playbook.triggerType} • ${widget.playbook.actions.length} action(s)',
          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: _isRunning
                  ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.bolt, color: AppColors.neonBlue),
              onPressed: _isRunning ? null : _run,
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline, color: AppColors.alertRed),
              onPressed: () => ref.read(playbookControllerProvider.notifier).delete(widget.playbook.id),
            ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 6,
                  children: widget.playbook.actions
                      .map((a) => Chip(label: Text(a.type, style: const TextStyle(fontSize: 11))))
                      .toList(),
                ),
                const SizedBox(height: 12),
                Text('Historique d\'exécution', style: Theme.of(context).textTheme.bodyMedium),
                const SizedBox(height: 8),
                runsAsync.when(
                  data: (runs) {
                    if (runs.isEmpty) return const Text('Aucune exécution.');
                    return Column(
                      children: runs.map((run) {
                        final color = run.status == 'COMPLETED'
                            ? AppColors.securityGreen
                            : run.status == 'FAILED'
                                ? AppColors.alertRed
                                : AppColors.warningAmber;
                        return ListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          leading: Icon(Icons.circle, size: 10, color: color),
                          title: Text('${run.status} • ${run.triggerSource}', style: const TextStyle(fontSize: 12)),
                          subtitle: Text(dateFormat.format(run.startedAt), style: const TextStyle(fontSize: 11)),
                        );
                      }).toList(),
                    );
                  },
                  error: (_, _) => const Text('Erreur de chargement des exécutions'),
                  loading: () => const Center(child: CircularProgressIndicator()),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
