import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../widgets/severity_badge.dart';
import '../application/incident_controller.dart';

class IncidentsScreen extends ConsumerWidget {
  const IncidentsScreen({super.key});

  void _showCreateDialog(BuildContext context, WidgetRef ref) {
    final titleController = TextEditingController();
    final descController = TextEditingController();
    String severity = 'MEDIUM';

    showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setState) => AlertDialog(
          title: const Text('Nouvel incident'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(controller: titleController, decoration: const InputDecoration(labelText: 'Titre')),
              const SizedBox(height: 12),
              TextField(
                controller: descController,
                decoration: const InputDecoration(labelText: 'Description'),
                maxLines: 3,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: severity,
                decoration: const InputDecoration(labelText: 'Sévérité'),
                items: const ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (value) => setState(() => severity = value ?? 'MEDIUM'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Annuler')),
            ElevatedButton(
              onPressed: () async {
                if (titleController.text.trim().isEmpty) return;
                await ref.read(incidentControllerProvider.notifier).create(
                      title: titleController.text.trim(),
                      description: descController.text.trim().isEmpty ? null : descController.text.trim(),
                      severity: severity,
                    );
                if (dialogContext.mounted) Navigator.of(dialogContext).pop();
              },
              child: const Text('Créer'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final incidentsAsync = ref.watch(incidentControllerProvider);
    final metricsAsync = ref.watch(incidentMetricsProvider);
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gestion des Incidents'),
        actions: [
          IconButton(icon: const Icon(Icons.add), onPressed: () => _showCreateDialog(context, ref)),
          const SizedBox(width: 12),
        ],
      ),
      body: Column(
        children: [
          metricsAsync.when(
            data: (metrics) => Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  _MetricChip(label: 'Total', value: '${metrics.total}'),
                  const SizedBox(width: 12),
                  _MetricChip(label: 'Ouverts', value: '${metrics.open}', color: AppColors.warningAmber),
                  const SizedBox(width: 12),
                  _MetricChip(label: 'Clos', value: '${metrics.closed}', color: AppColors.securityGreen),
                  const SizedBox(width: 12),
                  _MetricChip(
                    label: 'MTTR moyen',
                    value: metrics.mttrHours != null ? '${metrics.mttrHours!.toStringAsFixed(1)}h' : 'N/A',
                    color: AppColors.neonBlue,
                  ),
                ],
              ),
            ),
            error: (_, _) => const SizedBox.shrink(),
            loading: () => const Padding(
              padding: EdgeInsets.all(16),
              child: LinearProgressIndicator(),
            ),
          ),
          const Divider(height: 1, color: AppColors.borderColor),
          Expanded(
            child: incidentsAsync.when(
              data: (incidents) {
                if (incidents.isEmpty) {
                  return const Center(child: Text('Aucun incident enregistré.'));
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: incidents.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final incident = incidents[index];
                    return Card(
                      child: ListTile(
                        onTap: () => context.push('/incidents/${incident.id}'),
                        leading: SeverityBadge(severity: incident.severity),
                        title: Text(incident.title),
                        subtitle: Text(
                          '${incident.status} • ${dateFormat.format(incident.createdAt)}',
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
          ),
        ],
      ),
    );
  }
}

class _MetricChip extends StatelessWidget {
  const _MetricChip({required this.label, required this.value, this.color = AppColors.textPrimary});

  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(value, style: TextStyle(color: color, fontSize: 20, fontWeight: FontWeight.bold)),
              Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }
}
