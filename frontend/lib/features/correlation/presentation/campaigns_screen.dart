import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../application/correlation_providers.dart';

class CampaignsScreen extends ConsumerStatefulWidget {
  const CampaignsScreen({super.key});

  @override
  ConsumerState<CampaignsScreen> createState() => _CampaignsScreenState();
}

class _CampaignsScreenState extends ConsumerState<CampaignsScreen> {
  bool _isDetecting = false;

  Future<void> _detect() async {
    setState(() => _isDetecting = true);
    try {
      await ref.read(correlationServiceProvider).detect();
      ref.invalidate(campaignListProvider);
    } finally {
      if (mounted) setState(() => _isDetecting = false);
    }
  }

  Color _scoreColor(double score) {
    if (score >= 8) return AppColors.alertRed;
    if (score >= 5) return AppColors.warningAmber;
    return AppColors.securityGreen;
  }

  @override
  Widget build(BuildContext context) {
    final campaignsAsync = ref.watch(campaignListProvider);
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Corrélation de Menaces'),
        actions: [
          IconButton(
            tooltip: 'Détecter de nouvelles campagnes',
            icon: _isDetecting
                ? const SizedBox(
                    width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.hub_outlined),
            onPressed: _isDetecting ? null : _detect,
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: campaignsAsync.when(
        data: (campaigns) {
          if (campaigns.isEmpty) {
            return const Center(
              child: Text('Aucune campagne détectée. Lancez une détection.'),
            );
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: campaigns.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final campaign = campaigns[index];
              return Card(
                child: ListTile(
                  onTap: () => context.push('/correlation/${campaign.id}'),
                  leading: CircleAvatar(
                    backgroundColor: _scoreColor(campaign.threatScore).withValues(alpha: 0.15),
                    child: Text(
                      campaign.threatScore.toStringAsFixed(1),
                      style: TextStyle(
                        color: _scoreColor(campaign.threatScore),
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  title: Text(campaign.name),
                  subtitle: Text(
                    '${campaign.status} • depuis ${campaign.firstSeen != null ? dateFormat.format(campaign.firstSeen!) : 'N/A'}',
                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                  ),
                  trailing: const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                ),
              );
            },
          );
        },
        error: (e, _) => Center(child: Text('Erreur: $e')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}
