import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../core/theme/app_colors.dart';
import '../application/integrations_controller.dart';

class IntegrationsScreen extends ConsumerWidget {
  const IntegrationsScreen({super.key});

  Future<void> _createApiKey(BuildContext context, WidgetRef ref) async {
    final nameController = TextEditingController(text: 'Clé d\'intégration');
    final name = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Nouvelle clé API'),
        content: TextField(controller: nameController, decoration: const InputDecoration(labelText: 'Nom')),
        actions: [
          TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Annuler')),
          ElevatedButton(
            onPressed: () => Navigator.of(dialogContext).pop(nameController.text.trim()),
            child: const Text('Créer'),
          ),
        ],
      ),
    );
    if (name == null || name.isEmpty || !context.mounted) return;

    final rawKey = await ref.read(apiKeysProvider.notifier).create(name);
    if (!context.mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Clé API créée'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Copiez cette clé maintenant — elle ne sera plus jamais affichée.',
              style: TextStyle(color: AppColors.warningAmber),
            ),
            const SizedBox(height: 12),
            SelectableText(rawKey, style: const TextStyle(fontFamily: 'monospace')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Fermer')),
        ],
      ),
    );
  }

  Future<void> _createWebhook(BuildContext context, WidgetRef ref) async {
    final urlController = TextEditingController();
    String platform = 'SLACK';

    await showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setState) => AlertDialog(
          title: const Text('Nouveau webhook'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                initialValue: platform,
                decoration: const InputDecoration(labelText: 'Plateforme'),
                items: const ['SLACK', 'DISCORD', 'TEAMS', 'CUSTOM']
                    .map((p) => DropdownMenuItem(value: p, child: Text(p)))
                    .toList(),
                onChanged: (value) => setState(() => platform = value ?? 'SLACK'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: urlController,
                decoration: const InputDecoration(labelText: 'URL du webhook entrant'),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Annuler')),
            ElevatedButton(
              onPressed: () async {
                if (urlController.text.trim().isEmpty) return;
                await ref.read(webhooksProvider.notifier).create(platform: platform, url: urlController.text.trim());
                if (dialogContext.mounted) Navigator.of(dialogContext).pop();
              },
              child: const Text('Ajouter'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final apiKeysAsync = ref.watch(apiKeysProvider);
    final webhooksAsync = ref.watch(webhooksProvider);
    final dateFormat = DateFormat('dd/MM/yyyy HH:mm');

    return Scaffold(
      appBar: AppBar(title: const Text('API Publique & Webhooks')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Clés API', style: Theme.of(context).textTheme.titleMedium),
                ElevatedButton.icon(
                  onPressed: () => _createApiKey(context, ref),
                  icon: const Icon(Icons.key, size: 18),
                  label: const Text('Nouvelle clé'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            apiKeysAsync.when(
              data: (keys) => keys.isEmpty
                  ? const Text('Aucune clé API. Créez-en une pour intégrer CyberPulse à un script externe.')
                  : Column(
                      children: keys.map((key) {
                        return Card(
                          child: ListTile(
                            leading: Icon(
                              key.isActive ? Icons.vpn_key_outlined : Icons.key_off_outlined,
                              color: key.isActive ? AppColors.securityGreen : AppColors.textSecondary,
                            ),
                            title: Text(key.name),
                            subtitle: Text(
                              '${key.keyPrefix}••••••••  •  ${key.rateLimitPerMinute} req/min  •  '
                              '${key.lastUsedAt != null ? "utilisée le ${dateFormat.format(key.lastUsedAt!)}" : "jamais utilisée"}',
                              style: const TextStyle(fontSize: 12),
                            ),
                            trailing: key.isActive
                                ? TextButton(
                                    onPressed: () => ref.read(apiKeysProvider.notifier).revoke(key.id),
                                    child: const Text('Révoquer'),
                                  )
                                : const Chip(label: Text('Révoquée'), backgroundColor: AppColors.panelBlackAlt),
                          ),
                        );
                      }).toList(),
                    ),
              error: (e, _) => Text('Erreur: $e'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
            const SizedBox(height: 32),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Webhooks (Slack / Discord / Teams)', style: Theme.of(context).textTheme.titleMedium),
                ElevatedButton.icon(
                  onPressed: () => _createWebhook(context, ref),
                  icon: const Icon(Icons.add_link, size: 18),
                  label: const Text('Nouveau webhook'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            webhooksAsync.when(
              data: (webhooks) => webhooks.isEmpty
                  ? const Text('Aucun webhook configuré. Les nouvelles alertes y seront envoyées automatiquement.')
                  : Column(
                      children: webhooks.map((webhook) {
                        return Card(
                          child: ListTile(
                            leading: const Icon(Icons.webhook_outlined, color: AppColors.neonBlue),
                            title: Text(webhook.platform),
                            subtitle: Text(webhook.url, style: const TextStyle(fontSize: 12)),
                            trailing: IconButton(
                              icon: const Icon(Icons.delete_outline, color: AppColors.alertRed),
                              onPressed: () => ref.read(webhooksProvider.notifier).delete(webhook.id),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
              error: (e, _) => Text('Erreur: $e'),
              loading: () => const Center(child: CircularProgressIndicator()),
            ),
          ],
        ),
      ),
    );
  }
}
