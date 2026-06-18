import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/alert.dart';
import '../../../widgets/severity_badge.dart';
import '../application/alert_controller.dart';

class AlertsScreen extends ConsumerWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alertsAsync = ref.watch(alertControllerProvider);
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Centre d\'alertes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(alertControllerProvider.notifier).refresh(),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: alertsAsync.when(
        data: (alerts) {
          if (alerts.isEmpty) {
            return const Center(child: Text('Aucune alerte pour le moment'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: alerts.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (context, index) => _AlertRow(
              alert: alerts[index],
              dateFormat: dateFormat,
              onAcknowledge: () =>
                  ref.read(alertControllerProvider.notifier).acknowledge(alerts[index].id),
            ),
          );
        },
        error: (e, _) => Center(child: Text('Erreur: $e')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}

class _AlertRow extends StatelessWidget {
  const _AlertRow({required this.alert, required this.dateFormat, required this.onAcknowledge});

  final CyberAlert alert;
  final DateFormat dateFormat;
  final VoidCallback onAcknowledge;

  @override
  Widget build(BuildContext context) {
    final isNew = alert.status == 'NEW';
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            SeverityBadge(severity: alert.severity),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(alert.message),
                  const SizedBox(height: 4),
                  Text(
                    '${alert.type} • ${dateFormat.format(alert.createdAt)}',
                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                  ),
                ],
              ),
            ),
            if (isNew)
              TextButton(onPressed: onAcknowledge, child: const Text('Acquitter'))
            else
              const Chip(label: Text('Acquittée'), backgroundColor: AppColors.panelBlackAlt),
          ],
        ),
      ),
    );
  }
}
