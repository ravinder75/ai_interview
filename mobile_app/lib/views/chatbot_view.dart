import 'package:flutter/material.dart';

class MobileChatBotView extends StatefulWidget {
  const MobileChatBotView({super.key});

  @override
  State<MobileChatBotView> createState() => _MobileChatBotViewState();
}

class _MobileChatBotViewState extends State<MobileChatBotView> {
  final _messageController = TextEditingController();
  final List<Map<String, String>> _chatMessages = [
    {
      'sender': 'AI Assistant',
      'text': 'Hello! I am your AI Career & Technical Coach. Ask me anything about interview prep, DSA, or system design!'
    }
  ];

  void _sendMessage() {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _chatMessages.add({'sender': 'You', 'text': text});
      _messageController.clear();
      
      // Auto response
      _chatMessages.add({
        'sender': 'AI Assistant',
        'text': 'Great question about "$text"! Remember to structure your answer using the STAR method (Situation, Task, Action, Result).'
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('AI Career Chatbot', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _chatMessages.length,
              itemBuilder: (context, idx) {
                final msg = _chatMessages[idx];
                final isUser = msg['sender'] == 'You';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 6),
                    padding: const EdgeInsets.all(12),
                    constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                    decoration: BoxDecoration(
                      color: isUser ? const Color(0xFF4F46E5) : const Color(0xFF0F172A),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: isUser ? const Color(0xFF6366F1) : const Color(0xFF1E293B)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          msg['sender']!,
                          style: TextStyle(color: isUser ? Colors.white70 : const Color(0xFF818CF8), fontSize: 10, fontWeight: FontWeight.bold),
                        ),
                        const SizedBox(height: 4),
                        Text(msg['text']!, style: const TextStyle(color: Colors.white, fontSize: 12)),
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: const BoxDecoration(
              color: Color(0xFF0F172A),
              border: Border(top: BorderSide(color: Color(0xFF1E293B))),
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _messageController,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                    decoration: InputDecoration(
                      hintText: 'Ask AI Chatbot anything...',
                      hintStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                      filled: true,
                      fillColor: const Color(0xFF020617),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  onPressed: _sendMessage,
                  icon: const Icon(Icons.send_rounded, color: Color(0xFF818CF8)),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
