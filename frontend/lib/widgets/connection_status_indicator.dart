import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/providers/core_providers.dart';
import '../core/theme/app_colors.dart';

class ConnectionStatusIndicator extends ConsumerWidget {
  const ConnectionStatusIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final socket = ref.watch(webSocketServiceProvider);
    return StreamBuilder<bool>(
      stream: socket.connectionStatus,
      initialData: socket.isConnected,
      builder: (context, snapshot) {
        final connected = snapshot.data ?? false;
        final color = connected ? AppColors.securityGreen : AppColors.alertRed;
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: 6),
            Text(
              connected ? 'Live' : 'Hors-ligne',
              style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600),
            ),
          ],
        );
      },
    );
  }
}
