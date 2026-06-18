import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/mitre.dart';
import '../data/mitre_service.dart';

final mitreServiceProvider = Provider<MitreService>((ref) {
  return MitreService(ref.watch(dioClientProvider));
});

final attackMatrixProvider = FutureProvider.autoDispose<AttackMatrix>((ref) {
  return ref.watch(mitreServiceProvider).getMatrix();
});

final attackHeatmapProvider = FutureProvider.autoDispose<List<HeatmapEntry>>((ref) {
  return ref.watch(mitreServiceProvider).getHeatmap();
});
