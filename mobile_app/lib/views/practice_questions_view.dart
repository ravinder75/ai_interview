import 'package:flutter/material.dart';

class PracticeQuestionsView extends StatefulWidget {
  const PracticeQuestionsView({super.key});

  @override
  State<PracticeQuestionsView> createState() => _PracticeQuestionsViewState();
}

class _PracticeQuestionsViewState extends State<PracticeQuestionsView> {
  final List<Map<String, String>> _questions = [
    {
      'category': 'Behavioral',
      'title': 'Tell me about a time you faced a major technical challenge.',
      'diff': 'Medium',
    },
    {
      'category': 'System Design',
      'title': 'How would you design a scalable real-time chat application?',
      'diff': 'Hard',
    },
    {
      'category': 'Frontend / React',
      'title': 'Explain Virtual DOM diffing and React performance optimization.',
      'diff': 'Easy',
    },
    {
      'category': 'Backend / Python',
      'title': 'How does FastAPI handle async request processing with Uvicorn?',
      'diff': 'Medium',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Interview Practice Questions', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _questions.length,
        itemBuilder: (context, idx) {
          final q = _questions[idx];
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
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
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(color: Colors.indigo.shade900, borderRadius: BorderRadius.circular(6)),
                      child: Text(q['category']!, style: const TextStyle(color: Color(0xFF818CF8), fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                    Text(q['diff']!, style: const TextStyle(color: Colors.amber, fontSize: 10, fontWeight: FontWeight.bold)),
                  ],
                ),
                const SizedBox(height: 10),
                Text(q['title']!, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Starting practice for: ${q['category']}')),
                    );
                  },
                  icon: const Icon(Icons.play_arrow_rounded, size: 16),
                  label: const Text('Practice Answer Now', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF4F46E5),
                    foregroundColor: Colors.white,
                    minimumSize: const Size(double.infinity, 36),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
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
