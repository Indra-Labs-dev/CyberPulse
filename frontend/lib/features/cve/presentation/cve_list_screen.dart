import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/cve.dart';
import '../../../widgets/severity_badge.dart';
import '../application/cve_providers.dart';

const _severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];

class CveListScreen extends ConsumerStatefulWidget {
  const CveListScreen({super.key});

  @override
  ConsumerState<CveListScreen> createState() => _CveListScreenState();
}

class _CveListScreenState extends ConsumerState<CveListScreen> {
  final _searchController = TextEditingController();
  final _productController = TextEditingController();
  bool _isSyncing = false;

  @override
  void dispose() {
    _searchController.dispose();
    _productController.dispose();
    super.dispose();
  }

  void _applyFilters() {
    final filters = ref.read(cveFiltersProvider);
    ref.read(cveFiltersProvider.notifier).state = filters.copyWith(
      search: _searchController.text,
      product: _productController.text,
    );
  }

  Future<void> _syncCves() async {
    setState(() => _isSyncing = true);
    try {
      await ref.read(cveServiceProvider).sync(count: 10);
      ref.invalidate(cveListProvider);
    } finally {
      if (mounted) setState(() => _isSyncing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final cvesAsync = ref.watch(cveListProvider);
    final filters = ref.watch(cveFiltersProvider);
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Veille CVE'),
        actions: [
          IconButton(
            tooltip: 'Synchroniser depuis NVD/CISA',
            icon: _isSyncing
                ? const SizedBox(
                    width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.cloud_sync_outlined),
            onPressed: _isSyncing ? null : _syncCves,
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                SizedBox(
                  width: 260,
                  child: TextField(
                    controller: _searchController,
                    decoration: const InputDecoration(
                      labelText: 'Recherche',
                      prefixIcon: Icon(Icons.search),
                    ),
                    onSubmitted: (_) => _applyFilters(),
                  ),
                ),
                SizedBox(
                  width: 200,
                  child: TextField(
                    controller: _productController,
                    decoration: const InputDecoration(labelText: 'Produit'),
                    onSubmitted: (_) => _applyFilters(),
                  ),
                ),
                SizedBox(
                  width: 180,
                  child: DropdownButtonFormField<String?>(
                    initialValue: filters.severity,
                    decoration: const InputDecoration(labelText: 'Sévérité'),
                    items: [
                      const DropdownMenuItem(value: null, child: Text('Toutes')),
                      ..._severities.map((s) => DropdownMenuItem(value: s, child: Text(s))),
                    ],
                    onChanged: (value) {
                      ref.read(cveFiltersProvider.notifier).state =
                          filters.copyWith(severity: value, clearSeverity: value == null);
                    },
                  ),
                ),
                SizedBox(
                  width: 150,
                  child: TextField(
                    decoration: const InputDecoration(labelText: 'CVSS min'),
                    keyboardType: TextInputType.number,
                    onSubmitted: (value) {
                      ref.read(cveFiltersProvider.notifier).state =
                          filters.copyWith(cvssMin: double.tryParse(value));
                    },
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _applyFilters,
                  icon: const Icon(Icons.filter_alt_outlined, size: 18),
                  label: const Text('Filtrer'),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: AppColors.borderColor),
          Expanded(
            child: cvesAsync.when(
              data: (cves) {
                if (cves.isEmpty) {
                  return const Center(child: Text('Aucune CVE ne correspond aux filtres'));
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: cves.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) => _CveRow(
                    cve: cves[index],
                    dateFormat: dateFormat,
                    onTap: () => context.push('/cves/${cves[index].id}'),
                  ),
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

class _CveRow extends StatelessWidget {
  const _CveRow({required this.cve, required this.dateFormat, required this.onTap});

  final Cve cve;
  final DateFormat dateFormat;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              SeverityBadge(severity: cve.severity),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(cve.cveId,
                        style: const TextStyle(
                            color: AppColors.neonBlue, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text(cve.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                  ],
                ),
              ),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text('CVSS ${cve.cvssScore?.toStringAsFixed(1) ?? 'N/A'}',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  Text(
                    cve.publishedAt != null ? dateFormat.format(cve.publishedAt!) : '-',
                    style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
                  ),
                ],
              ),
              const Icon(Icons.chevron_right, color: AppColors.textSecondary),
            ],
          ),
        ),
      ),
    );
  }
}
