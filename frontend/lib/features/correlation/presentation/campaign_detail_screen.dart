import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/correlation.dart';
import '../application/correlation_providers.dart';

class CampaignDetailScreen extends ConsumerWidget {
  const CampaignDetailScreen({super.key, required this.campaignId});

  final int campaignId;

  Color _nodeColor(String type) {
    switch (type) {
      case 'ACTOR':
        return AppColors.alertRed;
      case 'CVE':
        return AppColors.neonBlue;
      case 'ARTICLE':
        return AppColors.securityGreen;
      default:
        return AppColors.warningAmber;
    }
  }

  IconData _nodeIcon(String type) {
    switch (type) {
      case 'ACTOR':
        return Icons.groups_outlined;
      case 'CVE':
        return Icons.bug_report_outlined;
      case 'ARTICLE':
        return Icons.article_outlined;
      default:
        return Icons.hub_outlined;
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final detailAsync = ref.watch(campaignDetailProvider(campaignId));
    final graphAsync = ref.watch(campaignGraphProvider(campaignId));
    final timelineAsync = ref.watch(campaignTimelineProvider(campaignId));
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(title: const Text('Détail Campagne')),
      body: detailAsync.when(
        data: (campaign) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 900),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(campaign.name, style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(height: 8),
                Text(campaign.description ?? '', style: const TextStyle(color: AppColors.textSecondary)),
                const SizedBox(height: 16),
                Wrap(
                  spacing: 24,
                  children: [
                    _StatTile(label: 'Score de menace', value: campaign.threatScore.toStringAsFixed(1)),
                    _StatTile(label: 'Statut', value: campaign.status),
                    if (campaign.actor != null)
                      _StatTile(label: 'Acteur présumé', value: campaign.actor!.name),
                  ],
                ),
                const SizedBox(height: 24),
                Text('Graphe de corrélation', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                graphAsync.when(
                  data: (graph) => _GraphView(
                    graph: graph,
                    nodeColor: _nodeColor,
                    nodeIcon: _nodeIcon,
                  ),
                  error: (_, _) => const Text('Erreur de chargement du graphe'),
                  loading: () => const Center(child: CircularProgressIndicator()),
                ),
                const SizedBox(height: 24),
                Text('Timeline de la campagne', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                timelineAsync.when(
                  data: (events) => Column(
                    children: events.map((event) {
                      return Card(
                        child: ListTile(
                          dense: true,
                          leading: Icon(_nodeIcon(event.type), color: _nodeColor(event.type), size: 20),
                          title: Text(event.label, style: const TextStyle(fontSize: 13)),
                          subtitle: Text(dateFormat.format(event.occurredAt),
                              style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)),
                        ),
                      );
                    }).toList(),
                  ),
                  error: (_, _) => const Text('Erreur de chargement de la timeline'),
                  loading: () => const Center(child: CircularProgressIndicator()),
                ),
              ],
            ),
          ),
        ),
        error: (e, _) => Center(child: Text('Erreur: $e')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _StatTile extends StatelessWidget {
  const _StatTile({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    );
  }
}

class _GraphView extends StatelessWidget {
  const _GraphView({required this.graph, required this.nodeColor, required this.nodeIcon});

  final CorrelationGraph graph;
  final Color Function(String) nodeColor;
  final IconData Function(String) nodeIcon;

  @override
  Widget build(BuildContext context) {
    final campaignNode = graph.nodes.firstWhere((n) => n.type == 'CAMPAIGN', orElse: () => graph.nodes.first);
    final otherNodes = graph.nodes.where((n) => n.id != campaignNode.id).toList();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Chip(
              avatar: Icon(nodeIcon('CAMPAIGN'), color: AppColors.neonBlue, size: 18),
              label: Text(campaignNode.label, style: const TextStyle(fontWeight: FontWeight.bold)),
              backgroundColor: AppColors.neonBlue.withValues(alpha: 0.12),
            ),
            const SizedBox(height: 16),
            const Icon(Icons.south, color: AppColors.textSecondary, size: 18),
            const SizedBox(height: 16),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              alignment: WrapAlignment.center,
              children: otherNodes.map((node) {
                return Chip(
                  avatar: Icon(nodeIcon(node.type), color: nodeColor(node.type), size: 16),
                  label: Text(node.label, style: const TextStyle(fontSize: 12)),
                  backgroundColor: nodeColor(node.type).withValues(alpha: 0.12),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}
