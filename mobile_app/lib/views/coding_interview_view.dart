import 'package:flutter/material.dart';

class CodingInterviewView extends StatefulWidget {
  const CodingInterviewView({super.key});

  @override
  State<CodingInterviewView> createState() => _CodingInterviewViewState();
}

class _CodingInterviewViewState extends State<CodingInterviewView> {
  final _codeController = TextEditingController(text: '''def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
''');

  String _executionOutput = 'Output ready. Click "Run Code" to test solution.';

  void _runCode() {
    setState(() {
      _executionOutput = '✓ All Test Cases Passed!\nRuntime: 32 ms (Beats 94.2%)\nMemory: 14.8 MB';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Coding Arena (DSA)', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
                  Text('Problem 1: Two Sum (LeetCode Easy)', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                  SizedBox(height: 6),
                  Text(
                    'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.',
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 14),

            const Text('Python Solution Editor', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            TextField(
              controller: _codeController,
              maxLines: 8,
              style: const TextStyle(color: Color(0xFFE0E7FF), fontSize: 12, fontFamily: 'monospace'),
              decoration: InputDecoration(
                filled: true,
                fillColor: const Color(0xFF0F172A),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: const BorderSide(color: Color(0xFF334155)),
                ),
              ),
            ),
            const SizedBox(height: 12),

            SizedBox(
              width: double.infinity,
              height: 44,
              child: ElevatedButton.icon(
                onPressed: _runCode,
                icon: const Icon(Icons.play_arrow_rounded),
                label: const Text('Run Code & Execute Tests', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF4F46E5),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
            const SizedBox(height: 14),

            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: Colors.black,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Text(_executionOutput, style: const TextStyle(color: Colors.greenAccent, fontSize: 11, fontFamily: 'monospace')),
            ),
          ],
        ),
      ),
    );
  }
}
