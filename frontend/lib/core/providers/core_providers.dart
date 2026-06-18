import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../features/auth/application/auth_controller.dart';
import '../../features/websocket/websocket_service.dart';
import '../network/dio_client.dart';
import '../storage/secure_storage_service.dart';

final secureStorageProvider = Provider<SecureStorageService>((ref) {
  return SecureStorageService();
});

final dioClientProvider = Provider<DioClient>((ref) {
  final storage = ref.watch(secureStorageProvider);
  return DioClient(
    storage,
    onSessionExpired: () => ref.read(authControllerProvider.notifier).forceLogout(),
  );
});

final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final storage = ref.watch(secureStorageProvider);
  final service = WebSocketService(storage);
  ref.onDispose(service.dispose);
  return service;
});
