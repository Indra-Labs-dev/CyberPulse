import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('App boots and shows the login screen', (WidgetTester tester) async {
    await tester.pumpWidget(const ProviderScope(child: CyberPulseApp()));
    await tester.pumpAndSettle();

    expect(find.text('CyberPulse'), findsWidgets);
    expect(find.text('Se connecter'), findsOneWidget);
  });
}
