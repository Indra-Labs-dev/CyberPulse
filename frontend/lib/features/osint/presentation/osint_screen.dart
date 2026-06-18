import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/osint.dart';
import '../application/osint_controller.dart';

class OsintScreen extends ConsumerStatefulWidget {
  const OsintScreen({super.key});

  @override
  ConsumerState<OsintScreen> createState() => _OsintScreenState();
}

class _OsintScreenState extends ConsumerState<OsintScreen> {
  final _targetController = TextEditingController();
  String _type = 'CERT_TRANSPARENCY';
  bool _isLooking = false;

  @override
  void dispose() {
    _targetController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_targetController.text.trim().isEmpty) return;
    setState(() => _isLooking = true);
    try {
      await ref.read(osintControllerProvider.notifier).lookup(
            type: _type,
            target: _targetController.text.trim(),
          );
      _targetController.clear();
    } finally {
      if (mounted) setState(() => _isLooking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final resultsAsync = ref.watch(osintControllerProvider);
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');
    const encoder = JsonEncoder.withIndent('  ');

    return Scaffold(
      appBar: AppBar(title: const Text('Veille OSINT')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Wrap(
              spacing: 12,
              runSpacing: 12,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                SizedBox(
                  width: 260,
                  child: DropdownButtonFormField<String>(
                    initialValue: _type,
                    decoration: const InputDecoration(labelText: 'Type de recherche'),
                    items: osintTypes
                        .map((t) => DropdownMenuItem(value: t, child: Text(osintTypeLabel(t))))
                        .toList(),
                    onChanged: (value) => setState(() => _type = value ?? _type),
                  ),
                ),
                SizedBox(
                  width: 280,
                  child: TextField(
                    controller: _targetController,
                    decoration: const InputDecoration(
                      labelText: 'Cible (email, IP, domaine, requête...)',
                    ),
                    onSubmitted: (_) => _submit(),
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _isLooking ? null : _submit,
                  icon: _isLooking
                      ? const SizedBox(
                          width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.travel_explore, size: 18),
                  label: const Text('Lancer'),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: AppColors.borderColor),
          Expanded(
            child: resultsAsync.when(
              data: (results) {
                if (results.isEmpty) {
                  return const Center(child: Text('Aucune recherche OSINT effectuée.'));
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: results.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final result = results[index];
                    final isPlaceholder = result.result is Map && result.result['status'] == 'placeholder';
                    return Card(
                      child: ExpansionTile(
                        leading: Icon(
                          isPlaceholder ? Icons.info_outline : Icons.check_circle_outline,
                          color: isPlaceholder ? AppColors.warningAmber : AppColors.securityGreen,
                        ),
                        title: Text('${osintTypeLabel(result.type)} — ${result.target}'),
                        subtitle: Text(
                          '${result.source} • ${dateFormat.format(result.scannedAt)}',
                          style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                        ),
                        children: [
                          Padding(
                            padding: const EdgeInsets.all(16),
                            child: SelectableText(
                              encoder.convert(result.result),
                              style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
                            ),
                          ),
                        ],
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
