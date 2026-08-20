import 'package:flutter/material.dart';

class NotificationsView extends StatelessWidget {
  const NotificationsView({super.key});

  final List<Map<String, String>> _notifications = const [
    {
      'title': 'Interview Scheduled Tomorrow',
      'body': 'Your Full-Stack Mock Interview with Sophia AI is set for tomorrow at 10:00 AM IST.',
      'time': '2 hours ago',
      'icon': 'calendar'
    },
    {
      'title': 'Resume Score Ready',
      'body': 'Your uploaded CV scored 88/100! Click here to view improvement tips.',
      'time': '1 day ago',
      'icon': 'description'
    },
    {
      'title': 'New Practice Question Added',
      'body': 'System Design: Design a Rate Limiter has been added to Practice Arena.',
      'time': '2 days ago',
      'icon': 'code'
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Notifications', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _notifications.length,
        itemBuilder: (context, idx) {
          final item = _notifications[idx];
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFF1E293B)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(color: const Color(0xFF1E1B4B), borderRadius: BorderRadius.circular(10)),
                  child: const Icon(Icons.notifications_active_rounded, color: Color(0xFF818CF8), size: 20),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(item['title']!, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
                          ),
                          Text(item['time']!, style: const TextStyle(color: Colors.grey, fontSize: 10)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(item['body']!, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                    ],
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
