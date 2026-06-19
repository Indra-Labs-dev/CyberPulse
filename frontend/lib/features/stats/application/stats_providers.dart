import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/stats.dart';
import '../data/stats_service.dart';

final statsServiceProvider = Provider<StatsService>((ref) {
  return StatsService(ref.watch(dioClientProvider));
});

final personalStatsProvider = FutureProvider.autoDispose<PersonalStats>((ref) {
  return ref.watch(statsServiceProvider).personal();
});

final teamStatsProvider = FutureProvider.autoDispose<TeamStats>((ref) {
  return ref.watch(statsServiceProvider).team();
});

final cveTrendsProvider = FutureProvider.autoDispose<List<TrendPoint>>((ref) {
  return ref.watch(statsServiceProvider).trends();
});
