import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/providers/core_providers.dart';
import '../../../models/collaboration.dart';
import '../data/collaboration_service.dart';

final collaborationServiceProvider = Provider<CollaborationService>((ref) {
  return CollaborationService(ref.watch(dioClientProvider));
});

final commentsProvider = FutureProvider.autoDispose
    .family<List<CyberComment>, ({String entityType, int entityId})>((ref, params) {
  return ref.watch(collaborationServiceProvider).listComments(
        entityType: params.entityType,
        entityId: params.entityId,
      );
});

final savedSearchesProvider = FutureProvider.autoDispose<List<SavedSearch>>((ref) {
  return ref.watch(collaborationServiceProvider).listSearches();
});

final activityFeedProvider = FutureProvider.autoDispose<List<ActivityLogEntry>>((ref) {
  return ref.watch(collaborationServiceProvider).listActivity();
});
