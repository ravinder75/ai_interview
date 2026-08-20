import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ResumeAnalyzerView extends StatefulWidget {
  const ResumeAnalyzerView({super.key});

  @override
  State<ResumeAnalyzerView> createState() => _ResumeAnalyzerViewState();
}

class _ResumeAnalyzerViewState extends State<ResumeAnalyzerView> {
  bool _isAnalyzing = false;
  Map<String, dynamic>? _analysisResult;

  void _simulateResumeUpload() async {
    setState(() => _isAnalyzing = true);
    await Future.delayed(const Duration(seconds: 2));
    setState(() {
      _isAnalyzing = false;
      _analysisResult = {
        'candidate_name': 'Ravinder Nyalakanti',
        'target_role': 'Full-Stack Developer',
        'resume_score': 88,
        'matched_skills': ['Flutter (Dart)', 'Vue 3', 'Python FastAPI', 'REST APIs', 'Database Design'],
        'missing_skills': ['Kubernetes', 'GraphQL'],
        'recommendations': [
          'Highlight quantitative system performance metrics in your project descriptions.',
          'Add a dedicated System Architecture & Distributed Systems section.'
        ]
      };
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('AI Resume Analyzer', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: const Color(0xFF1E293B)),
              ),
              child: Column(
                children: [
                  const Icon(Icons.description_rounded, color: Color(0xFF818CF8), size: 40),
                  const SizedBox(height: 12),
                  const Text('Upload & Analyze Candidate Resume', style: TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  const Text('Upload PDF or Word document for instant AI skills matching & feedback', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11), textAlign: TextAlign.center),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    height: 44,
                    child: ElevatedButton.icon(
                      onPressed: _isAnalyzing ? null : _simulateResumeUpload,
                      icon: _isAnalyzing
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                          : const Icon(Icons.upload_file_rounded, size: 18),
                      label: Text(_isAnalyzing ? 'Analyzing Resume...' : 'Upload & Analyze Resume', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF4F46E5),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            if (_analysisResult != null) ...[
              const SizedBox(height: 20),
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(_analysisResult!['candidate_name'], style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.indigo.shade900,
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.indigoAccent),
                          ),
                          child: Text('Score: ${_analysisResult!['resume_score']}/100', style: const TextStyle(color: Colors.indigoAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    const Text('Matched Core Skills:', style: TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 6,
                      children: (_analysisResult!['matched_skills'] as List<String>).map((skill) {
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.green.shade900.withOpacity(0.4),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: Colors.green.shade700),
                          ),
                          child: Text('✓ $skill', style: const TextStyle(color: Colors.greenAccent, fontSize: 11, fontWeight: FontWeight.bold)),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
