import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/vuln_scan.dart';
import '../application/scanner_controller.dart';

class ScannerScreen extends ConsumerStatefulWidget {
  const ScannerScreen({super.key});

  @override
  ConsumerState<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends ConsumerState<ScannerScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabController;
  final _targetController = TextEditingController(text: '127.0.0.1');
  final _portsController = TextEditingController();
  final _scheduleController = TextEditingController();
  final _fileNameController = TextEditingController(text: 'config.env');
  final _fileContentController = TextEditingController();
  bool _isRunning = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _targetController.dispose();
    _portsController.dispose();
    _scheduleController.dispose();
    _fileNameController.dispose();
    _fileContentController.dispose();
    super.dispose();
  }

  Future<void> _runPortScan() async {
    setState(() => _isRunning = true);
    try {
      final ports = _portsController.text.trim().isEmpty
          ? null
          : _portsController.text.split(',').map((p) => int.tryParse(p.trim())).whereType<int>().toList();
      final schedule = int.tryParse(_scheduleController.text.trim());
      await ref.read(scannerControllerProvider.notifier).runPortScan(
            target: _targetController.text.trim(),
            ports: ports,
            scheduleMinutes: schedule,
          );
    } finally {
      if (mounted) setState(() => _isRunning = false);
    }
  }

  Future<void> _runFileScan() async {
    if (_fileContentController.text.trim().isEmpty) return;
    setState(() => _isRunning = true);
    try {
      await ref.read(scannerControllerProvider.notifier).runFileScan(
            filename: _fileNameController.text.trim(),
            content: _fileContentController.text,
          );
      _fileContentController.clear();
    } finally {
      if (mounted) setState(() => _isRunning = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final scansAsync = ref.watch(scannerControllerProvider);
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scanner Léger'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: 'Scan Port/IP'),
            Tab(text: 'Scan de fichier'),
          ],
        ),
      ),
      body: Column(
        children: [
          SizedBox(
            height: 260,
            child: TabBarView(
              controller: _tabController,
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Wrap(
                    spacing: 12,
                    runSpacing: 12,
                    children: [
                      SizedBox(
                        width: 200,
                        child: TextField(
                          controller: _targetController,
                          decoration: const InputDecoration(labelText: 'Cible (IP/hôte)'),
                        ),
                      ),
                      SizedBox(
                        width: 220,
                        child: TextField(
                          controller: _portsController,
                          decoration:
                              const InputDecoration(labelText: 'Ports (ex: 22,80,443) — vide = ports courants'),
                        ),
                      ),
                      SizedBox(
                        width: 200,
                        child: TextField(
                          controller: _scheduleController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: 'Récurrence (minutes, optionnel)'),
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: _isRunning ? null : _runPortScan,
                        icon: _isRunning
                            ? const SizedBox(
                                width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                            : const Icon(Icons.radar, size: 18),
                        label: const Text('Scanner'),
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          SizedBox(
                            width: 220,
                            child: TextField(
                              controller: _fileNameController,
                              decoration: const InputDecoration(labelText: 'Nom du fichier'),
                            ),
                          ),
                          const SizedBox(width: 12),
                          ElevatedButton.icon(
                            onPressed: _isRunning ? null : _runFileScan,
                            icon: const Icon(Icons.search, size: 18),
                            label: const Text('Analyser'),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Expanded(
                        child: TextField(
                          controller: _fileContentController,
                          maxLines: null,
                          expands: true,
                          decoration: const InputDecoration(
                            labelText: 'Collez le contenu du fichier de configuration à analyser',
                            alignLabelWithHint: true,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: AppColors.borderColor),
          Expanded(
            child: scansAsync.when(
              data: (scans) {
                if (scans.isEmpty) {
                  return const Center(child: Text('Aucun scan effectué.'));
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: scans.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) => _ScanResultCard(scan: scans[index], dateFormat: dateFormat),
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

class _ScanResultCard extends StatelessWidget {
  const _ScanResultCard({required this.scan, required this.dateFormat});

  final VulnScan scan;
  final DateFormat dateFormat;

  @override
  Widget build(BuildContext context) {
    final isPortScan = scan.scanType == 'PORT_SCAN';
    return Card(
      child: ExpansionTile(
        leading: Icon(
          isPortScan ? Icons.lan_outlined : Icons.description_outlined,
          color: scan.findings.isNotEmpty ? AppColors.warningAmber : AppColors.securityGreen,
        ),
        title: Text(scan.target),
        subtitle: Text(
          '${scan.scanType} • ${scan.findings.length} résultat(s) • ${dateFormat.format(scan.createdAt)}'
          '${scan.scheduleMinutes != null ? ' • récurrent (${scan.scheduleMinutes}min)' : ''}',
          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
        ),
        children: scan.findings.map<Widget>((finding) {
          if (isPortScan) {
            final f = finding as Map<String, dynamic>;
            return ListTile(
              dense: true,
              leading: const Icon(Icons.circle, size: 10, color: AppColors.securityGreen),
              title: Text('Port ${f['port']} — ${f['service']}'),
              subtitle: Text(
                [
                  if (f['banner'] != null) 'Bannière: ${f['banner']}',
                  if ((f['matched_cves'] as List).isNotEmpty)
                    'CVE: ${(f['matched_cves'] as List).join(', ')}',
                ].join(' • '),
                style: const TextStyle(fontSize: 11),
              ),
            );
          } else {
            final f = finding as Map<String, dynamic>;
            return ListTile(
              dense: true,
              leading: const Icon(Icons.warning_amber, size: 16, color: AppColors.alertRed),
              title: Text(f['issue'] as String),
              subtitle: Text('Ligne ${f['line']} : ${f['excerpt']}', style: const TextStyle(fontSize: 11)),
            );
          }
        }).toList(),
      ),
    );
  }
}
