import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../widgets/severity_badge.dart';
import '../../collaboration/presentation/comments_section.dart';
import '../application/cve_providers.dart';

class CveDetailScreen extends ConsumerWidget {
  const CveDetailScreen({super.key, required this.cveId});

  final int cveId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cveAsync = ref.watch(cveDetailProvider(cveId));
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(title: const Text('Détail CVE')),
      body: cveAsync.when(
        data: (cve) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 900),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(cve.cveId,
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(color: AppColors.neonBlue, fontWeight: FontWeight.bold)),
                    const SizedBox(width: 16),
                    SeverityBadge(severity: cve.severity),
                  ],
                ),
                const SizedBox(height: 8),
                Text(cve.title, style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 24),
                Wrap(
                  spacing: 24,
                  runSpacing: 16,
                  children: [
                    _InfoTile(label: 'Score CVSS', value: cve.cvssScore?.toStringAsFixed(1) ?? 'N/A'),
                    _InfoTile(label: 'Vecteur CVSS', value: cve.cvssVector ?? 'N/A'),
                    _InfoTile(label: 'CWE', value: cve.cweId ?? 'N/A'),
                    _InfoTile(label: 'Source', value: cve.source),
                    _InfoTile(
                      label: 'Publié le',
                      value: cve.publishedAt != null ? dateFormat.format(cve.publishedAt!) : 'N/A',
                    ),
                    _InfoTile(
                      label: 'Modifié le',
                      value: cve.modifiedAt != null ? dateFormat.format(cve.modifiedAt!) : 'N/A',
                    ),
                  ],
                ),
                const SizedBox(height: 24),
                Text('Description', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 8),
                Text(cve.description ?? 'Aucune description disponible',
                    style: const TextStyle(color: AppColors.textSecondary)),
                const SizedBox(height: 24),
                if (cve.affectedProducts.isNotEmpty) ...[
                  Text('Produits affectés', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    children: cve.affectedProducts
                        .map((p) => Chip(label: Text(p), backgroundColor: AppColors.panelBlackAlt))
                        .toList(),
                  ),
                  const SizedBox(height: 24),
                ],
                if (cve.references.isNotEmpty) ...[
                  Text('Références', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  ...cve.references.map(
                    (r) => Padding(
                      padding: const EdgeInsets.only(bottom: 4),
                      child: Text(r, style: const TextStyle(color: AppColors.neonBlue)),
                    ),
                  ),
                  const SizedBox(height: 24),
                ],
                CommentsSection(entityType: 'CVE', entityId: cve.id),
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

class _InfoTile extends StatelessWidget {
  const _InfoTile({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 200,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
          const SizedBox(height: 4),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}
