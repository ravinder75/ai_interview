import 'package:flutter/material.dart';

class MobileDashboardView extends StatelessWidget {
  final VoidCallback onNavigateToMock;
  final VoidCallback onNavigateToPractice;
  final VoidCallback onNavigateToResume;
  final VoidCallback onNavigateToJobAnalysis;

  const MobileDashboardView({
    super.key,
    required this.onNavigateToMock,
    required this.onNavigateToPractice,
    required this.onNavigateToResume,
    required this.onNavigateToJobAnalysis,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Dashboard & Overview', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Hero Banner
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF0F172A), Color(0xFF1E1B4B)]),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(color: const Color(0xFF4F46E5).withValues(alpha: 0.2), borderRadius: BorderRadius.circular(20)),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.auto_awesome_rounded, color: Color(0xFF818CF8), size: 14),
                        SizedBox(width: 6),
                        Text('Welcome to AI Interview Coach', style: TextStyle(color: Color(0xFF818CF8), fontSize: 11, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text('Master Technical & Behavioral Skills', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  const Text('Simulate real-time AI mock interviews, practice STAR questions, and score resumes with 100% ATS optimization.',
                      style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11, height: 1.4)),
                  const SizedBox(height: 16),
                  const Text('Interview Readiness Score', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(10),
                    child: LinearProgressIndicator(
                      value: 0.88,
                      minHeight: 10,
                      backgroundColor: const Color(0xFF020617),
                      color: const Color(0xFF34D399),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            const Text('Quick Action Launchpad', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),

            // Action Launchpad Grid
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 1.25,
              children: [
                _buildActionCard(
                  icon: Icons.video_call_rounded,
                  color: Colors.indigo,
                  title: 'Start Mock',
                  subtitle: 'Simulate Live Room',
                  onTap: onNavigateToMock,
                ),
                _buildActionCard(
                  icon: Icons.play_circle_fill_rounded,
                  color: Colors.purple,
                  title: 'Practice Questions',
                  subtitle: 'Explore Category Bank',
                  onTap: onNavigateToPractice,
                ),
                _buildActionCard(
                  icon: Icons.description_rounded,
                  color: Colors.green,
                  title: 'Resume Builder',
                  subtitle: '100% ATS Analyzer',
                  onTap: onNavigateToResume,
                ),
                _buildActionCard(
                  icon: Icons.work_rounded,
                  color: Colors.cyan,
                  title: 'Analyze Job Post',
                  subtitle: 'Live Matching Engine',
                  onTap: onNavigateToJobAnalysis,
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Recent Session Ratings
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFF1E293B)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Recent Session Ratings & Performance', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  _buildSessionRow('Backend Systems & Microservices', 'Software Engineer • Aug 15', '92%'),
                  const Divider(color: Color(0xFF1E293B)),
                  _buildSessionRow('System Architecture & APIs', 'Senior Full-Stack • Aug 14', '85%'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard({
    required IconData icon,
    required MaterialColor color,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF1E293B)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: color.shade400, size: 24),
            const SizedBox(height: 8),
            Text(title, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
            const SizedBox(height: 2),
            Text(subtitle, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 10)),
          ],
        ),
      ),
    );
  }

  Widget _buildSessionRow(String title, String subtitle, String score) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                Text(subtitle, style: const TextStyle(color: Colors.grey, fontSize: 10)),
              ],
            ),
          ),
          Text(score, style: const TextStyle(color: Color(0xFF34D399), fontSize: 14, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
        ],
      ),
    );
  }
}
