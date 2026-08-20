import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:ai_interview_coach_mobile/main.dart';
import 'package:ai_interview_coach_mobile/core/auth/auth_provider.dart';

void main() {
  testWidgets('App renders login screen smoke test', (WidgetTester tester) async {
    final authProvider = AuthProvider();
    
    await tester.pumpWidget(
      ChangeNotifierProvider<AuthProvider>.value(
        value: authProvider,
        child: const AiInterviewCoachApp(),
      ),
    );
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });
}
