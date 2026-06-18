import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/incident.dart';
import '../../../widgets/severity_badge.dart';
import '../application/incident_controller.dart';

class IncidentDetailScreen extends ConsumerWidget {
  const IncidentDetailScreen({super.key, required this.incidentId});

  final int incidentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incidentAsync = ref.watch(incidentDetailProvider(incidentId));
    final activityAsync = ref.watch(incidentActivityProvider(incidentId));
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(title: const Text('Détail Incident')),
      body: incidentAsync.when(
        data: (incident) => SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 900),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                        child: Text(incident.title, style: Theme.of(context).textTheme.headlineSmall)),
                    SeverityBadge(severity: incident.severity),
                  ],
                ),
                const SizedBox(height: 8),
                Text(incident.description ?? 'Aucune description',
                    style: const TextStyle(color: AppColors.textSecondary)),
                const SizedBox(height: 24),
                Text('Workflow de réponse', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                _WorkflowStepper(currentStatus: incident.status, incidentId: incidentId),
                const SizedBox(height: 24),
                Text('Journal d\'activité', style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 12),
                activityAsync.when(
                  data: (activities) => Column(
                    children: activities.map((a) {
                      return Card(
                        child: ListTile(
                          dense: true,
                          leading: const Icon(Icons.history, color: AppColors.neonBlue, size: 20),
                          title: Text(a.message, style: const TextStyle(fontSize: 13)),
                          subtitle: Text(
                            '${a.action} • ${dateFormat.format(a.createdAt)}',
                            style: const TextStyle(fontSize: 11, color: AppColors.textSecondary),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                  error: (_, _) => const Text('Erreur de chargement du journal'),
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

class _WorkflowStepper extends ConsumerWidget {
  const _WorkflowStepper({required this.currentStatus, required this.incidentId});

  final String currentStatus;
  final int incidentId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIndex = incidentWorkflow.indexOf(currentStatus);

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: incidentWorkflow.asMap().entries.map((entry) {
        final index = entry.key;
        final status = entry.value;
        final isDone = index < currentIndex;
        final isCurrent = index == currentIndex;
        final color = isCurrent
            ? AppColors.neonBlue
            : isDone
                ? AppColors.securityGreen
                : AppColors.textSecondary;

        return ActionChip(
          avatar: Icon(
            isDone ? Icons.check_circle : Icons.radio_button_unchecked,
            color: color,
            size: 16,
          ),
          label: Text(status, style: TextStyle(color: color, fontSize: 12)),
          backgroundColor: isCurrent ? AppColors.neonBlue.withValues(alpha: 0.12) : AppColors.panelBlackAlt,
          onPressed: () async {
            await ref.read(incidentControllerProvider.notifier).updateStatus(incidentId, status);
            ref.invalidate(incidentDetailProvider(incidentId));
            ref.invalidate(incidentActivityProvider(incidentId));
            ref.invalidate(incidentMetricsProvider);
          },
        );
      }).toList(),
    );
  }
}
