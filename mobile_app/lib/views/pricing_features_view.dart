import 'package:flutter/material.dart';

class PricingAndFeaturesView extends StatelessWidget {
  const PricingAndFeaturesView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Plans & App Features', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Pro Plan Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF1E1B4B), Color(0xFF0F172A)]),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF6366F1), width: 1.5),
              ),
              child: Column(
                children: [
                  const Text('PRO CANDIDATE PLAN', style: TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Text('\$19 / month', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  const Text('• Unlimited AI Mock Interviews\n• Full Resume Analysis & Feedback\n• Interview-Bit Chrome Extension Access\n• Priority OpenRouter AI Response Time',
                      style: TextStyle(color: Color(0xFFCBD5E1), fontSize: 12, height: 1.5)),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4F46E5),
                      foregroundColor: Colors.white,
                      minimumSize: const Size(double.infinity, 42),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: const Text('Upgrade to Pro Plan', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // About Platform
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF1E293B)),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('About AI Interview Coach', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text(
                    'AI Mock Interview Coach is a cross-platform solution providing real-time AI live mock sessions, DSA coding arena practice, resume scoring, and interview scheduling across Web & Mobile.',
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11, height: 1.4),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
