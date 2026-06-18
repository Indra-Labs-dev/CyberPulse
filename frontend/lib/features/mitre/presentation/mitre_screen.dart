import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../application/mitre_providers.dart';

class MitreScreen extends ConsumerWidget {
  const MitreScreen({super.key});

  Color _intensityColor(int count, int maxCount) {
    if (maxCount == 0 || count == 0) return AppColors.panelBlackAlt;
    final ratio = count / maxCount;
    return Color.lerp(AppColors.panelBlackAlt, AppColors.alertRed, ratio.clamp(0.15, 1.0))!;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final matrixAsync = ref.watch(attackMatrixProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Matrice MITRE ATT&CK'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(attackMatrixProvider),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: matrixAsync.when(
        data: (matrix) {
          final maxCount = matrix.tactics.values
              .expand((entries) => entries)
              .map((e) => e.mappedCveCount)
              .fold(0, (a, b) => a > b ? a : b);

          return SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Wrap(
              spacing: 16,
              runSpacing: 16,
              children: matrix.tactics.entries.map((tacticEntry) {
                return SizedBox(
                  width: 260,
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            tacticEntry.key,
                            style: const TextStyle(
                                color: AppColors.neonBlue, fontWeight: FontWeight.bold),
                          ),
                          const Divider(color: AppColors.borderColor),
                          ...tacticEntry.value.map((entry) {
                            return Container(
                              margin: const EdgeInsets.only(bottom: 6),
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                              decoration: BoxDecoration(
                                color: _intensityColor(entry.mappedCveCount, maxCount),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      '${entry.technique.techniqueId} — ${entry.technique.name}',
                                      style: const TextStyle(fontSize: 12),
                                      maxLines: 2,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  if (entry.mappedCveCount > 0)
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                      decoration: BoxDecoration(
                                        color: AppColors.deepBlack.withValues(alpha: 0.4),
                                        borderRadius: BorderRadius.circular(10),
                                      ),
                                      child: Text(
                                        '${entry.mappedCveCount}',
                                        style: const TextStyle(fontSize: 11, color: AppColors.textPrimary),
                                      ),
                                    ),
                                ],
                              ),
                            );
                          }),
                        ],
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          );
        },
        error: (e, _) => Center(child: Text('Erreur: $e')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}
