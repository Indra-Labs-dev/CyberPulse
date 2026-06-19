import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/stats.dart';
import '../../../widgets/kpi_card.dart';
import '../application/stats_providers.dart';

class StatsScreen extends ConsumerWidget {
  const StatsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final personalAsync = ref.watch(personalStatsProvider);
    final teamAsync = ref.watch(teamStatsProvider);
    final trendsAsync = ref.watch(cveTrendsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Statistiques & Analytics')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Mes statistiques', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            personalAsync.when(
              data: (stats) => GridView.count(
                crossAxisCount: 5,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: 1.3,
                children: [
                  KpiCard(
                      label: 'Rapports créés',
                      value: '${stats.reportsCreated}',
                      icon: Icons.description_outlined,
                      accentColor: AppColors.neonBlue),
                  KpiCard(
                      label: 'Incidents créés',
                      value: '${stats.incidentsCreated}',
                      icon: Icons.report_problem_outlined,
                      accentColor: AppColors.alertRed),
                  KpiCard(
                      label: 'Alertes acquittées',
                      value: '${stats.alertsAcknowledged}',
                      icon: Icons.notifications_active_outlined,
                      accentColor: AppColors.securityGreen),
                  KpiCard(
                      label: 'Produits surveillés',
                      value: '${stats.watchlistEntries}',
                      icon: Icons.visibility_outlined,
                      accentColor: AppColors.warningAmber),
                  KpiCard(
                      label: 'Commentaires',
                      value: '${stats.commentsPosted}',
                      icon: Icons.comment_outlined,
                      accentColor: AppColors.neonBlue),
                ],
              ),
              error: (e, _) => Text('Erreur: $e'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
            const SizedBox(height: 32),
            Text('Statistiques de l\'équipe', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            teamAsync.when(
              data: (stats) => GridView.count(
                crossAxisCount: 6,
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                mainAxisSpacing: 16,
                crossAxisSpacing: 16,
                childAspectRatio: 1.3,
                children: [
                  KpiCard(
                      label: 'CVE totales',
                      value: '${stats.totalCves}',
                      icon: Icons.bug_report_outlined,
                      accentColor: AppColors.neonBlue),
                  KpiCard(
                      label: 'Incidents ouverts',
                      value: '${stats.openIncidents}/${stats.totalIncidents}',
                      icon: Icons.report_problem_outlined,
                      accentColor: AppColors.alertRed),
                  KpiCard(
                      label: 'Rapports',
                      value: '${stats.totalReports}',
                      icon: Icons.description_outlined,
                      accentColor: AppColors.securityGreen),
                  KpiCard(
                      label: 'Alertes',
                      value: '${stats.totalAlerts}',
                      icon: Icons.notifications_outlined,
                      accentColor: AppColors.warningAmber),
                  KpiCard(
                      label: 'Articles scrapés',
                      value: '${stats.totalArticles}',
                      icon: Icons.article_outlined,
                      accentColor: AppColors.neonBlue),
                  KpiCard(
                      label: 'MTTR moyen',
                      value: stats.avgIncidentResolutionHours != null
                          ? '${stats.avgIncidentResolutionHours!.toStringAsFixed(1)}h'
                          : 'N/A',
                      icon: Icons.timer_outlined,
                      accentColor: AppColors.securityGreen),
                ],
              ),
              error: (e, _) => Text('Erreur: $e'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
            const SizedBox(height: 32),
            Text('Évolution des CVE publiées (30 derniers jours)',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: SizedBox(
                  height: 300,
                  child: trendsAsync.when(
                    data: (points) {
                      if (points.isEmpty) {
                        return const Center(child: Text('Aucune donnée pour cette période'));
                      }
                      return SfCartesianChart(
                        primaryXAxis: DateTimeAxis(),
                        series: <CartesianSeries>[
                          LineSeries<TrendPoint, DateTime>(
                            dataSource: points,
                            xValueMapper: (p, _) => p.date,
                            yValueMapper: (p, _) => p.count,
                            color: AppColors.neonBlue,
                            markerSettings: const MarkerSettings(isVisible: true),
                          ),
                        ],
                      );
                    },
                    error: (e, _) => Text('Erreur: $e'),
                    loading: () => const Center(child: CircularProgressIndicator()),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
