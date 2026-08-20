import 'package:flutter/material.dart';

class MobileJobAnalysisView extends StatefulWidget {
  const MobileJobAnalysisView({super.key});

  @override
  State<MobileJobAnalysisView> createState() => _MobileJobAnalysisViewState();
}

class _MobileJobAnalysisViewState extends State<MobileJobAnalysisView> {
  final List<Map<String, dynamic>> _jobMatches = [
    {
      'company': 'Google India',
      'title': 'Senior Full-Stack Engineer',
      'match': 94,
      'location': 'Hyderabad / Remote',
      'type': 'Full-time',
      'matchedSkills': ['React', 'Python', 'FastAPI', 'System Design'],
      'missingSkills': ['GraphQL'],
    },
    {
      'company': 'Microsoft',
      'title': 'AI Solutions Architect',
      'match': 89,
      'location': 'Bengaluru, India',
      'type': 'Full-time',
      'matchedSkills': ['PyTorch', 'Gemini API', 'Docker'],
      'missingSkills': ['Kubernetes'],
    },
    {
      'company': 'Uber',
      'title': 'Mobile Engineer (Flutter)',
      'match': 91,
      'location': 'Remote (India)',
      'type': 'Contract',
      'matchedSkills': ['Flutter', 'Dart', 'REST API', 'State Management'],
      'missingSkills': ['BLoC Pattern'],
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Job Description & Live Matching', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _jobMatches.length,
        itemBuilder: (context, idx) {
          final job = _jobMatches[idx];
          return Container(
            margin: const EdgeInsets.only(bottom: 14),
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF1E293B)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(job['company'], style: const TextStyle(color: Colors.indigoAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(color: Colors.green.shade900, borderRadius: BorderRadius.circular(10)),
                      child: Text('${job['match']}% Match', style: const TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(job['title'], style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text('📍 ${job['location']} • 💼 ${job['type']}', style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                const SizedBox(height: 12),
                const Text('Matched Skills:', style: TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Wrap(
                  spacing: 6,
                  runSpacing: 4,
                  children: (job['matchedSkills'] as List<String>).map((sk) {
                    return Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: Colors.indigo.shade900.withValues(alpha: 0.5), borderRadius: BorderRadius.circular(6)),
                      child: Text('✓ $sk', style: const TextStyle(color: Color(0xFF818CF8), fontSize: 10)),
                    );
                  }).toList(),
                ),
                const SizedBox(height: 14),
                SizedBox(
                  width: double.infinity,
                  height: 38,
                  child: ElevatedButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Applying to ${job['company']} (${job['title']})...')),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4F46E5),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: const Text('Apply Now', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
