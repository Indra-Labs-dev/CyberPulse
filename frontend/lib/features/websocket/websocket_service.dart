import 'dart:async';

import 'package:socket_io_client/socket_io_client.dart' as io;

import '../../core/config/app_config.dart';
import '../../core/storage/secure_storage_service.dart';

/// Maintains the realtime connection to the CyberPulse backend (python-socketio)
/// and exposes broadcast streams for `alert` and `new_article` events.
class WebSocketService {
  WebSocketService(this._storage);

  final SecureStorageService _storage;

  io.Socket? _socket;

  final _alertController = StreamController<Map<String, dynamic>>.broadcast();
  final _articleController = StreamController<Map<String, dynamic>>.broadcast();
  final _connectionController = StreamController<bool>.broadcast();

  Stream<Map<String, dynamic>> get onAlert => _alertController.stream;
  Stream<Map<String, dynamic>> get onNewArticle => _articleController.stream;
  Stream<bool> get connectionStatus => _connectionController.stream;

  bool get isConnected => _socket?.connected ?? false;

  Future<void> connect() async {
    if (_socket != null && _socket!.connected) return;

    final token = await _storage.getAccessToken();

    _socket = io.io(
      AppConfig.socketUrl,
      io.OptionBuilder()
          .setTransports(['websocket'])
          .setPath('/socket.io')
          .setExtraHeaders(token != null ? {'Authorization': 'Bearer $token'} : {})
          .disableAutoConnect()
          .build(),
    );

    _socket!
      ..onConnect((_) => _connectionController.add(true))
      ..onDisconnect((_) => _connectionController.add(false))
      ..onConnectError((_) => _connectionController.add(false))
      ..on('alert', (data) {
        if (data is Map<String, dynamic>) _alertController.add(data);
      })
      ..on('new_article', (data) {
        if (data is Map<String, dynamic>) _articleController.add(data);
      })
      ..connect();
  }

  void disconnect() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
  }

  void dispose() {
    disconnect();
    _alertController.close();
    _articleController.close();
    _connectionController.close();
  }
}
