import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

import '../../../core/theme/app_colors.dart';
import '../../../widgets/kpi_card.dart';
import '../../../widgets/severity_badge.dart';
import '../../alerts/application/alert_controller.dart';
import '../../articles/application/article_controller.dart';
import '../../cve/application/cve_providers.dart';

class _SeverityCount {
  _SeverityCount(this.severity, this.count);
  final String severity;
  final int count;
}

class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cvesAsync = ref.watch(cveListProvider);
    final alertsAsync = ref.watch(alertControllerProvider);
    final articlesAsync = ref.watch(articleControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Synchroniser CVE',
            icon: const Icon(Icons.sync),
            onPressed: () => ref.invalidate(cveListProvider),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(cveListProvider);
          await ref.read(alertControllerProvider.notifier).refresh();
          await ref.read(articleControllerProvider.notifier).refresh();
        },
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            cvesAsync.when(
              data: (cves) {
                final critical = cves.where((c) => c.severity == 'CRITICAL').length;
                final high = cves.where((c) => c.severity == 'HIGH').length;
                return GridView.count(
                  crossAxisCount: 4,
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 1.4,
                  children: [
                    KpiCard(
                      label: 'CVE suivies',
                      value: '${cves.length}',
                      icon: Icons.bug_report_outlined,
                      accentColor: AppColors.neonBlue,
                    ),
                    KpiCard(
                      label: 'Critiques',
                      value: '$critical',
                      icon: Icons.warning_amber_rounded,
                      accentColor: AppColors.alertRed,
                    ),
                    KpiCard(
                      label: 'Sévérité haute',
                      value: '$high',
                      icon: Icons.priority_high,
                      accentColor: AppColors.warningAmber,
                    ),
                    KpiCard(
                      label: 'Alertes actives',
                      value: '${alertsAsync.valueOrNull?.where((a) => a.status == 'NEW').length ?? 0}',
                      icon: Icons.notifications_active_outlined,
                      accentColor: AppColors.securityGreen,
                    ),
                  ],
                );
              },
              error: (e, _) => Text('Erreur de chargement: $e'),
              loading: () => const SizedBox(
                height: 120,
                child: Center(child: CircularProgressIndicator()),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  flex: 3,
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Répartition par sévérité', style: Theme.of(context).textTheme.titleMedium),
                          const SizedBox(height: 12),
                          SizedBox(
                            height: 280,
                            child: cvesAsync.when(
                              data: (cves) {
                                final counts = <String, int>{};
                                for (final c in cves) {
                                  final key = c.severity ?? 'INCONNU';
                                  counts[key] = (counts[key] ?? 0) + 1;
                                }
                                final data = counts.entries
                                    .map((e) => _SeverityCount(e.key, e.value))
                                    .toList();
                                return SfCircularChart(
                                  legend: const Legend(isVisible: true, position: LegendPosition.bottom),
                                  series: <CircularSeries>[
                                    DoughnutSeries<_SeverityCount, String>(
                                      dataSource: data,
                                      xValueMapper: (d, _) => d.severity,
                                      yValueMapper: (d, _) => d.count,
                                      pointColorMapper: (d, _) => AppColors.severityColor(d.severity),
                                      dataLabelSettings: const DataLabelSettings(isVisible: true),
                                    ),
                                  ],
                                );
                              },
                              error: (_, _) => const Center(child: Text('Aucune donnée')),
                              loading: () => const Center(child: CircularProgressIndicator()),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  flex: 2,
                  child: Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Flux temps réel', style: Theme.of(context).textTheme.titleMedium),
                          const SizedBox(height: 12),
                          SizedBox(
                            height: 280,
                            child: alertsAsync.when(
                              data: (alerts) => alerts.isEmpty
                                  ? const Center(child: Text('Aucune alerte récente'))
                                  : ListView.separated(
                                      itemCount: alerts.length > 8 ? 8 : alerts.length,
                                      separatorBuilder: (_, _) =>
                                          const Divider(color: AppColors.borderColor),
                                      itemBuilder: (context, index) {
                                        final alert = alerts[index];
                                        return ListTile(
                                          dense: true,
                                          contentPadding: EdgeInsets.zero,
                                          leading: SeverityBadge(severity: alert.severity),
                                          title: Text(
                                            alert.message,
                                            maxLines: 2,
                                            overflow: TextOverflow.ellipsis,
                                            style: const TextStyle(fontSize: 13),
                                          ),
                                        );
                                      },
                                    ),
                              error: (_, _) => const Center(child: Text('Erreur')),
                              loading: () => const Center(child: CircularProgressIndicator()),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Derniers articles cyber', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 12),
                    articlesAsync.when(
                      data: (articles) => articles.isEmpty
                          ? const Text('Aucun article scrapé pour le moment')
                          : Column(
                              children: articles.take(5).map((article) {
                                return ListTile(
                                  contentPadding: EdgeInsets.zero,
                                  leading: const Icon(Icons.article_outlined, color: AppColors.neonBlue),
                                  title: Text(article.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                                  subtitle: Text('${article.source} • ${article.category ?? 'N/A'}'),
                                );
                              }).toList(),
                            ),
                      error: (_, _) => const Text('Erreur de chargement des articles'),
                      loading: () => const Center(child: CircularProgressIndicator()),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
