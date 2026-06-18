import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/correlation.dart';
import '../data/correlation_service.dart';

final correlationServiceProvider = Provider<CorrelationService>((ref) {
  return CorrelationService(ref.watch(dioClientProvider));
});

final campaignListProvider = FutureProvider.autoDispose<List<Campaign>>((ref) {
  return ref.watch(correlationServiceProvider).listCampaigns();
});

final threatActorListProvider = FutureProvider.autoDispose<List<ThreatActor>>((ref) {
  return ref.watch(correlationServiceProvider).listActors();
});

final campaignDetailProvider = FutureProvider.autoDispose.family<CampaignDetail, int>((ref, id) {
  return ref.watch(correlationServiceProvider).getCampaign(id);
});

final campaignGraphProvider = FutureProvider.autoDispose.family<CorrelationGraph, int>((ref, id) {
  return ref.watch(correlationServiceProvider).getGraph(id);
});

final campaignTimelineProvider = FutureProvider.autoDispose.family<List<TimelineEvent>, int>((ref, id) {
  return ref.watch(correlationServiceProvider).getTimeline(id);
});
