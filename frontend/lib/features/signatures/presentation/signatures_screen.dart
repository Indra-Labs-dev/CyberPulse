import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:open_filex/open_filex.dart';

import '../../../core/theme/app_colors.dart';
import '../../../models/signature.dart';
import '../application/signature_controller.dart';

class SignaturesScreen extends ConsumerStatefulWidget {
  const SignaturesScreen({super.key});

  @override
  ConsumerState<SignaturesScreen> createState() => _SignaturesScreenState();
}

class _SignaturesScreenState extends ConsumerState<SignaturesScreen> with SingleTickerProviderStateMixin {
  late final TabController _tabController;

  final _yaraName = TextEditingController(text: 'Suspicious_Dropper');
  final _yaraDescription = TextEditingController();
  final _yaraStrings = TextEditingController();
  final _yaraHashes = TextEditingController();

  final _sigmaName = TextEditingController(text: 'Suspicious PowerShell Execution');
  final _sigmaDescription = TextEditingController();
  final _sigmaSelection = TextEditingController(text: 'Image|endswith: \\powershell.exe\nCommandLine|contains: -enc');
  String _sigmaLevel = 'medium';

  bool _isGenerating = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _yaraName.dispose();
    _yaraDescription.dispose();
    _yaraStrings.dispose();
    _yaraHashes.dispose();
    _sigmaName.dispose();
    _sigmaDescription.dispose();
    _sigmaSelection.dispose();
    super.dispose();
  }

  Future<void> _generateYara() async {
    setState(() => _isGenerating = true);
    try {
      final strings = _yaraStrings.text.split('\n').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
      final hashes = _yaraHashes.text.split('\n').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
      await ref.read(signatureControllerProvider.notifier).generateYara(
            name: _yaraName.text.trim(),
            description: _yaraDescription.text.trim().isEmpty ? null : _yaraDescription.text.trim(),
            strings: strings,
            hashes: hashes,
          );
    } finally {
      if (mounted) setState(() => _isGenerating = false);
    }
  }

  Future<void> _generateSigma() async {
    setState(() => _isGenerating = true);
    try {
      final detectionSelection = <String, dynamic>{};
      for (final line in _sigmaSelection.text.split('\n')) {
        final parts = line.split(':');
        if (parts.length >= 2) {
          detectionSelection[parts[0].trim()] = parts.sublist(1).join(':').trim();
        }
      }
      await ref.read(signatureControllerProvider.notifier).generateSigma(
            name: _sigmaName.text.trim(),
            description: _sigmaDescription.text.trim().isEmpty ? null : _sigmaDescription.text.trim(),
            logSource: const {'category': 'process_creation', 'product': 'windows'},
            detectionSelection: detectionSelection,
            level: _sigmaLevel,
          );
    } finally {
      if (mounted) setState(() => _isGenerating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final signaturesAsync = ref.watch(signatureControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Signatures YARA / Sigma'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [Tab(text: 'Générateur YARA'), Tab(text: 'Générateur Sigma')],
        ),
      ),
      body: Column(
        children: [
          SizedBox(
            height: 320,
            child: TabBarView(
              controller: _tabController,
              children: [
                SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      TextField(controller: _yaraName, decoration: const InputDecoration(labelText: 'Nom de la règle')),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _yaraDescription,
                        decoration: const InputDecoration(labelText: 'Description'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _yaraStrings,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          labelText: 'Chaînes à détecter (une par ligne)',
                          alignLabelWithHint: true,
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _yaraHashes,
                        maxLines: 2,
                        decoration: const InputDecoration(
                          labelText: 'Hashes MD5/SHA1/SHA256 (un par ligne)',
                          alignLabelWithHint: true,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ElevatedButton.icon(
                        onPressed: _isGenerating ? null : _generateYara,
                        icon: const Icon(Icons.shield_outlined, size: 18),
                        label: const Text('Générer la règle YARA'),
                      ),
                    ],
                  ),
                ),
                SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      TextField(controller: _sigmaName, decoration: const InputDecoration(labelText: 'Titre de la règle')),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _sigmaDescription,
                        decoration: const InputDecoration(labelText: 'Description'),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _sigmaSelection,
                        maxLines: 3,
                        decoration: const InputDecoration(
                          labelText: 'Critères de détection (champ: valeur, une par ligne)',
                          alignLabelWithHint: true,
                        ),
                      ),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<String>(
                        initialValue: _sigmaLevel,
                        decoration: const InputDecoration(labelText: 'Niveau de sévérité'),
                        items: const ['low', 'medium', 'high', 'critical']
                            .map((l) => DropdownMenuItem(value: l, child: Text(l)))
                            .toList(),
                        onChanged: (value) => setState(() => _sigmaLevel = value ?? 'medium'),
                      ),
                      const SizedBox(height: 12),
                      ElevatedButton.icon(
                        onPressed: _isGenerating ? null : _generateSigma,
                        icon: const Icon(Icons.security_outlined, size: 18),
                        label: const Text('Générer la règle Sigma'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1, color: AppColors.borderColor),
          Expanded(
            child: signaturesAsync.when(
              data: (signatures) {
                if (signatures.isEmpty) {
                  return const Center(child: Text('Aucune signature générée.'));
                }
                return ListView.separated(
                  padding: const EdgeInsets.all(16),
                  itemCount: signatures.length,
                  separatorBuilder: (_, _) => const SizedBox(height: 8),
                  itemBuilder: (context, index) => _SignatureCard(signature: signatures[index]),
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

class _SignatureCard extends ConsumerWidget {
  const _SignatureCard({required this.signature});

  final SignatureRule signature;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      child: ExpansionTile(
        leading: Icon(
          signature.isValid ? Icons.verified_outlined : Icons.error_outline,
          color: signature.isValid ? AppColors.securityGreen : AppColors.alertRed,
        ),
        title: Text(signature.name),
        subtitle: Text('${signature.type} • ${signature.isValid ? "Valide" : "Invalide"}'),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.download_outlined),
              onPressed: () async {
                final path = await ref.read(signatureServiceProvider).download(signature);
                await OpenFilex.open(path);
              },
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline, color: AppColors.alertRed),
              onPressed: () => ref.read(signatureControllerProvider.notifier).delete(signature.id),
            ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: SelectableText(
              signature.ruleText,
              style: const TextStyle(fontFamily: 'monospace', fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }
}
