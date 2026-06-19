import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:open_filex/open_filex.dart';

import '../../../core/providers/core_providers.dart';
import '../../../core/theme/app_colors.dart';
import '../data/import_export_service.dart';

final importExportServiceProvider = Provider<ImportExportService>((ref) {
  return ImportExportService(ref.watch(dioClientProvider));
});

class ImportExportScreen extends ConsumerStatefulWidget {
  const ImportExportScreen({super.key});

  @override
  ConsumerState<ImportExportScreen> createState() => _ImportExportScreenState();
}

class _ImportExportScreenState extends ConsumerState<ImportExportScreen> {
  final _importController = TextEditingController(
    text: '[{"cve_id": "CVE-2026-10001", "title": "Exemple importé", "cvss_score": 8.2, "severity": "HIGH"}]',
  );
  String _importFormat = 'json';
  bool _isBusy = false;
  String? _lastResultMessage;

  @override
  void dispose() {
    _importController.dispose();
    super.dispose();
  }

  Future<void> _import() async {
    setState(() => _isBusy = true);
    try {
      final bytes = utf8.encode(_importController.text);
      final service = ref.read(importExportServiceProvider);
      final result = _importFormat == 'json'
          ? await service.importCvesJson('import.json', bytes)
          : await service.importCvesCsv('import.csv', bytes);
      setState(() => _lastResultMessage =
          'Importé: ${result['imported']}, Mis à jour: ${result['updated']}, Erreurs: ${(result['errors'] as List).length}');
    } catch (e) {
      setState(() => _lastResultMessage = 'Erreur: $e');
    } finally {
      if (mounted) setState(() => _isBusy = false);
    }
  }

  Future<void> _export(String format) async {
    setState(() => _isBusy = true);
    try {
      final path = await ref.read(importExportServiceProvider).exportCves(format);
      await OpenFilex.open(path);
    } finally {
      if (mounted) setState(() => _isBusy = false);
    }
  }

  Future<void> _backup() async {
    setState(() => _isBusy = true);
    try {
      final path = await ref.read(importExportServiceProvider).backup();
      await OpenFilex.open(path);
    } finally {
      if (mounted) setState(() => _isBusy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Import / Export')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Importer des CVE', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        DropdownButton<String>(
                          value: _importFormat,
                          items: const [
                            DropdownMenuItem(value: 'json', child: Text('JSON (NVD-like)')),
                            DropdownMenuItem(value: 'csv', child: Text('CSV')),
                          ],
                          onChanged: (value) => setState(() => _importFormat = value ?? 'json'),
                        ),
                        const SizedBox(width: 12),
                        ElevatedButton.icon(
                          onPressed: _isBusy ? null : _import,
                          icon: const Icon(Icons.upload_file, size: 18),
                          label: const Text('Importer'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _importController,
                      maxLines: 6,
                      style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                      decoration: const InputDecoration(
                        labelText: 'Contenu à importer',
                        alignLabelWithHint: true,
                      ),
                    ),
                    if (_lastResultMessage != null) ...[
                      const SizedBox(height: 8),
                      Text(_lastResultMessage!, style: const TextStyle(color: AppColors.securityGreen)),
                    ],
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            Text('Exporter les CVE', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                _ExportButton(label: 'JSON', icon: Icons.data_object, onPressed: () => _export('json')),
                _ExportButton(label: 'CSV', icon: Icons.table_chart_outlined, onPressed: () => _export('csv')),
                _ExportButton(label: 'XML', icon: Icons.code, onPressed: () => _export('xml')),
                _ExportButton(label: 'STIX 2.1', icon: Icons.hub_outlined, onPressed: () => _export('stix')),
                _ExportButton(label: 'MISP', icon: Icons.security_outlined, onPressed: () => _export('misp')),
                _ExportButton(label: 'OpenIOC', icon: Icons.fingerprint_outlined, onPressed: () => _export('openioc')),
              ],
            ),
            const SizedBox(height: 24),
            Text('Sauvegarde', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'Exporte un instantané JSON des CVE, watchlists et articles. '
                        'Réimportable via l\'import JSON ci-dessus.',
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: _isBusy ? null : _backup,
                      icon: const Icon(Icons.backup_outlined, size: 18),
                      label: const Text('Sauvegarder'),
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

class _ExportButton extends StatelessWidget {
  const _ExportButton({required this.label, required this.icon, required this.onPressed});

  final String label;
  final IconData icon;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return OutlinedButton.icon(onPressed: onPressed, icon: Icon(icon, size: 18), label: Text(label));
  }
}
