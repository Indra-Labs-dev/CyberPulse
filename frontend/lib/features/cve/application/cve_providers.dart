import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/cve.dart';
import '../data/cve_service.dart';

final cveServiceProvider = Provider<CveService>((ref) {
  return CveService(ref.watch(dioClientProvider));
});

final cveFiltersProvider = StateProvider<CveFilters>((ref) => const CveFilters());

final cveListProvider = FutureProvider.autoDispose<List<Cve>>((ref) async {
  final service = ref.watch(cveServiceProvider);
  final filters = ref.watch(cveFiltersProvider);
  return service.list(filters: filters, pageSize: 50);
});

final cveDetailProvider = FutureProvider.autoDispose.family<Cve, int>((ref, id) async {
  final service = ref.watch(cveServiceProvider);
  return service.getById(id);
});
