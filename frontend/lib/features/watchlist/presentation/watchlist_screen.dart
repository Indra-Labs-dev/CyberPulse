import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/app_colors.dart';
import '../application/watchlist_controller.dart';

class WatchlistScreen extends ConsumerWidget {
  const WatchlistScreen({super.key});

  void _showAddDialog(BuildContext context, WidgetRef ref) {
    final productController = TextEditingController();
    final vendorController = TextEditingController();
    String threshold = 'MEDIUM';

    showDialog<void>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, setState) => AlertDialog(
          title: const Text('Ajouter un produit surveillé'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: productController,
                decoration: const InputDecoration(labelText: 'Produit (ex: Nginx)'),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: vendorController,
                decoration: const InputDecoration(labelText: 'Éditeur (optionnel)'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                initialValue: threshold,
                decoration: const InputDecoration(labelText: 'Seuil d\'alerte'),
                items: const ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
                    .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                    .toList(),
                onChanged: (value) => setState(() => threshold = value ?? 'MEDIUM'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('Annuler'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (productController.text.trim().isEmpty) return;
                await ref.read(watchlistControllerProvider.notifier).add(
                      productName: productController.text.trim(),
                      vendor: vendorController.text.trim().isEmpty
                          ? null
                          : vendorController.text.trim(),
                      alertThreshold: threshold,
                    );
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
    final watchlistAsync = ref.watch(watchlistControllerProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Watchlist'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddDialog(context, ref),
          ),
          const SizedBox(width: 12),
        ],
      ),
      body: watchlistAsync.when(
        data: (entries) {
          if (entries.isEmpty) {
            return const Center(child: Text('Aucun produit surveillé. Ajoutez-en un.'));
          }
          return ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: entries.length,
            separatorBuilder: (_, _) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final entry = entries[index];
              return Card(
                child: ListTile(
                  leading: const Icon(Icons.visibility_outlined, color: AppColors.neonBlue),
                  title: Text(entry.productName),
                  subtitle: Text(entry.vendor ?? 'Éditeur inconnu'),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Chip(
                        label: Text(entry.alertThreshold),
                        backgroundColor: AppColors.panelBlackAlt,
                      ),
                      IconButton(
                        icon: const Icon(Icons.delete_outline, color: AppColors.alertRed),
                        onPressed: () =>
                            ref.read(watchlistControllerProvider.notifier).remove(entry.id),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
        error: (e, _) => Center(child: Text('Erreur: $e')),
        loading: () => const Center(child: CircularProgressIndicator()),
      ),
    );
  }
}
