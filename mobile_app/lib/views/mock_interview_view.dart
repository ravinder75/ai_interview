import 'package:flutter/material.dart';
import '../models/app_models.dart';
import '../services/api_service.dart';
import '../core/network/network_service.dart';

class MockInterviewView extends StatefulWidget {
  final UserSettings userSettings;
  const MockInterviewView({super.key, required this.userSettings});

  @override
  State<MockInterviewView> createState() => _MockInterviewViewState();
}

class _MockInterviewViewState extends State<MockInterviewView> {
  bool _isSessionActive = false;
  bool _isLoading = false;
  bool _isStealthMode = false;
  String _selectedRole = 'Full-Stack Developer';
  String _selectedExperience = '3-5 Years';

  final List<String> _roles = [
    'Full-Stack Developer',
    'AI/ML Engineer',
    'Flutter Mobile Developer',
    'Frontend Developer',
    'Backend Developer',
    'Medical Officer / Physician',
    'Product Manager',
  ];

  final List<Map<String, String>> _messages = [];

  void _startLiveInterview() async {
    if (_isSessionActive) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('⚠️ You already have an active live interview session for $_selectedRole. Please complete or end that session first.'),
          backgroundColor: Colors.orange.shade800,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    final isConnected = await NetworkService().checkConnection();
    if (!isConnected) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('⚡ Internet connection required for live AI mock interview.'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
      return;
    }

    final res = await ApiService.createInterviewSession(
      role: _selectedRole,
      experienceLevel: _selectedExperience,
      candidateName: widget.userSettings.candidateName,
    );

    setState(() {
      _isLoading = false;
      _isSessionActive = true;
      _messages.clear();
      _messages.add({
        'sender': 'Sophia AI',
        'text': 'Hello ${widget.userSettings.candidateName}! Welcome to your live $_selectedRole mock interview. Let us begin with your technical background and key contributions.'
      });
    });
  }

  void _endLiveInterview() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('End Live Interview?', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        content: const Text('Are you sure you want to finish this live session and generate your evaluation report?', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              setState(() {
                _isSessionActive = false;
                _messages.clear();
              });
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('✓ Live Interview Ended. Report generated!'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('End Session', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('AI Live Mock Room', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: Icon(_isStealthMode ? Icons.visibility_off_rounded : Icons.visibility_rounded, color: _isStealthMode ? Colors.amberAccent : Colors.white70),
            tooltip: _isStealthMode ? 'Stealth Mode Active (100% Invisible)' : 'Enable Stealth Mode (100% Invisible)',
            onPressed: () {
              setState(() {
                _isStealthMode = !_isStealthMode;
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_isStealthMode ? '👻 Stealth Mode Activated (100% Invisible)' : '👁️ Visible Mode Activated'),
                  duration: const Duration(seconds: 2),
                  backgroundColor: _isStealthMode ? Colors.amber.shade900 : Colors.indigo.shade800,
                ),
              );
            },
          ),
          if (_isSessionActive)
            Padding(
              padding: const EdgeInsets.only(right: 12),
              child: TextButton.icon(
                onPressed: _endLiveInterview,
                icon: const Icon(Icons.stop_circle_rounded, color: Colors.redAccent, size: 18),
                label: const Text('End Session', style: TextStyle(color: Colors.redAccent, fontSize: 12, fontWeight: FontWeight.bold)),
              ),
            ),
        ],
      ),
      body: !_isSessionActive
          ? SingleChildScrollView(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0F172A),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF1E293B)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Center(
                          child: Text('🤖 AI MOCK INTERVIEW', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                        ),
                        const SizedBox(height: 16),
                        const Text('Target Candidate Role', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 6),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12),
                          decoration: BoxDecoration(
                            color: const Color(0xFF020617),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: const Color(0xFF334155)),
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                              value: _selectedRole,
                              dropdownColor: const Color(0xFF0F172A),
                              isExpanded: true,
                              items: _roles.map((r) => DropdownMenuItem(value: r, child: Text(r, style: const TextStyle(color: Colors.white, fontSize: 12)))).toList(),
                              onChanged: (val) {
                                if (val != null) setState(() => _selectedRole = val);
                              },
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),
                        SizedBox(
                          width: double.infinity,
                          height: 48,
                          child: ElevatedButton.icon(
                            onPressed: _isLoading ? null : _startLiveInterview,
                            icon: _isLoading
                                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                                : const Icon(Icons.play_circle_fill_rounded),
                            label: const Text('[ START LIVE INTERVIEW ]', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
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
                ],
              ),
            )
          : Column(
              children: [
                // Live Stream Camera & Mic Preview Box
                Container(
                  height: 200,
                  margin: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.black,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF4F46E5)),
                  ),
                  child: Stack(
                    children: [
                      const Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.videocam_rounded, color: Colors.greenAccent, size: 32),
                            SizedBox(height: 4),
                            Text('YOU (Live Webcam Feed)', style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold)),
                          ],
                        ),
                      ),
                      Positioned(
                        top: 10,
                        right: 10,
                        child: Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                          decoration: BoxDecoration(color: Colors.black.withValues(alpha: 0.7), borderRadius: BorderRadius.circular(8)),
                          child: const Row(
                            children: [
                              Icon(Icons.fiber_manual_record_rounded, color: Colors.redAccent, size: 10),
                              SizedBox(width: 4),
                              Text('REC LIVE', style: TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
                            ],
                          ),
                        ),
                      ),
                      Positioned(
                        bottom: 10,
                        left: 10,
                        right: 10,
                        child: Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: const Color(0xFF0F172A).withValues(alpha: 0.9),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFF334155)),
                          ),
                          child: const Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                children: [
                                  Icon(Icons.mic_rounded, color: Colors.greenAccent, size: 14),
                                  SizedBox(width: 4),
                                  Text('MIC ON', style: TextStyle(color: Colors.greenAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                                ],
                              ),
                              Row(
                                children: [
                                  Icon(Icons.graphic_eq_rounded, color: Color(0xFF818CF8), size: 14),
                                  SizedBox(width: 4),
                                  Text('STATUS: LISTENING & TRANSCRIBING...', style: TextStyle(color: Color(0xFF818CF8), fontSize: 9, fontWeight: FontWeight.bold, fontFamily: 'monospace')),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                // QnA Stream History (Supports 100% Stealth Invisible Mode)
                Expanded(
                  child: AnimatedOpacity(
                    opacity: _isStealthMode ? 0.0 : 1.0,
                    duration: const Duration(milliseconds: 200),
                    child: ListView.builder(
                      padding: const EdgeInsets.all(12),
                      itemCount: _messages.length,
                      itemBuilder: (context, idx) {
                      final msg = _messages[idx];
                      final isAi = msg['sender'] == 'Sophia AI';
                      return Container(
                        margin: const EdgeInsets.symmetric(vertical: 6),
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isAi ? const Color(0xFF1E1B4B) : const Color(0xFF0F172A),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: isAi ? const Color(0xFF6366F1) : const Color(0xFF334155)),
                        ),
                        child: Text(
                          '${msg['sender']}: ${msg['text']}',
                          style: TextStyle(color: isAi ? const Color(0xFFE0E7FF) : Colors.white, fontSize: 12),
                        ),
                      );
                    },
                  ),
                ),
              ),
            ],
          ),
    );
  }
}
