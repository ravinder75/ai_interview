import 'package:flutter/material.dart';

class InterviewScheduleView extends StatefulWidget {
  const InterviewScheduleView({super.key});

  @override
  State<InterviewScheduleView> createState() => _InterviewScheduleViewState();
}

class _InterviewScheduleViewState extends State<InterviewScheduleView> {
  final List<Map<String, dynamic>> _scheduledInterviews = [
    {
      'id': 'sched-def8ef91-2e72-46e9-8175-48bedfbc0395',
      'title': 'Senior Full-Stack Developer Mock Interview',
      'role': 'Full-Stack Developer',
      'interviewer': 'Sophia AI',
      'time': 'Aug 19, 2026 • 10:00 AM',
      'status': 'Scheduled',
    },
    {
      'id': 'sched-8912ab34-1c23-44e9-9182-1234567890ab',
      'title': 'AI System Design & Distributed Systems',
      'role': 'AI/ML Engineer',
      'interviewer': 'Daniel AI',
      'time': 'Aug 20, 2026 • 02:30 PM',
      'status': 'Scheduled',
    },
  ];

  void _openScheduleModal() {
    final titleController = TextEditingController();
    String selectedRole = 'Full-Stack Developer';
    DateTime selectedDate = DateTime.now().add(const Duration(days: 1));
    TimeOfDay selectedTime = const TimeOfDay(hour: 10, minute: 0);

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setModalState) => AlertDialog(
          backgroundColor: const Color(0xFF0F172A),
          title: const Text('Schedule New AI Interview', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Interview Title', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: titleController,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: InputDecoration(
                    hintText: 'e.g. System Design Practice',
                    hintStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                    filled: true,
                    fillColor: const Color(0xFF020617),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10), borderSide: const BorderSide(color: Color(0xFF334155))),
                  ),
                ),
                const SizedBox(height: 12),
                const Text('Target Role', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(color: const Color(0xFF020617), borderRadius: BorderRadius.circular(10), border: Border.all(color: const Color(0xFF334155))),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: selectedRole,
                      dropdownColor: const Color(0xFF0F172A),
                      isExpanded: true,
                      items: ['Full-Stack Developer', 'AI/ML Engineer', 'Flutter Mobile Developer', 'Frontend Developer', 'Backend Developer']
                          .map((r) => DropdownMenuItem(value: r, child: Text(r, style: const TextStyle(color: Colors.white, fontSize: 12))))
                          .toList(),
                      onChanged: (val) {
                        if (val != null) setModalState(() => selectedRole = val);
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextButton.icon(
                        onPressed: () async {
                          final picked = await showDatePicker(
                            context: context,
                            initialDate: selectedDate,
                            firstDate: DateTime.now(),
                            lastDate: DateTime.now().add(const Duration(days: 90)),
                          );
                          if (picked != null) setModalState(() => selectedDate = picked);
                        },
                        icon: const Icon(Icons.calendar_month_rounded, size: 16, color: Color(0xFF818CF8)),
                        label: Text('${selectedDate.month}/${selectedDate.day}/${selectedDate.year}', style: const TextStyle(color: Colors.white, fontSize: 11)),
                      ),
                    ),
                    Expanded(
                      child: TextButton.icon(
                        onPressed: () async {
                          final picked = await showTimePicker(context: context, initialTime: selectedTime);
                          if (picked != null) setModalState(() => selectedTime = picked);
                        },
                        icon: const Icon(Icons.access_time_rounded, size: 16, color: Color(0xFF818CF8)),
                        label: Text(selectedTime.format(context), style: const TextStyle(color: Colors.white, fontSize: 11)),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel', style: TextStyle(color: Colors.grey)),
            ),
            ElevatedButton(
              onPressed: () {
                final title = titleController.text.trim().isEmpty ? '$selectedRole Practice Session' : titleController.text.trim();
                final formattedTime = '${selectedDate.month}/${selectedDate.day}/${selectedDate.year} • ${selectedTime.format(context)}';
                setState(() {
                  _scheduledInterviews.insert(0, {
                    'id': 'sched-${DateTime.now().millisecondsSinceEpoch}',
                    'title': title,
                    'role': selectedRole,
                    'interviewer': 'Sophia AI',
                    'time': formattedTime,
                    'status': 'Scheduled',
                  });
                });
                Navigator.pop(ctx);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('✓ Interview Scheduled Successfully!'), backgroundColor: Colors.green),
                );
              },
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF4F46E5)),
              child: const Text('Confirm Schedule', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text('Scheduled Interviews', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            onPressed: _openScheduleModal,
            icon: const Icon(Icons.add_circle_rounded, color: Color(0xFF818CF8)),
            tooltip: 'Schedule New Interview',
          ),
        ],
      ),
      body: _scheduledInterviews.isEmpty
          ? const Center(
              child: Text('No interviews scheduled yet. Tap + to add one!', style: TextStyle(color: Colors.grey, fontSize: 12)),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _scheduledInterviews.length,
              itemBuilder: (context, idx) {
                final sched = _scheduledInterviews[idx];
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
                          Text(sched['role'], style: const TextStyle(color: Color(0xFF818CF8), fontSize: 11, fontWeight: FontWeight.bold)),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.indigo.shade900.withValues(alpha: 0.5),
                              borderRadius: BorderRadius.circular(6),
                              border: Border.all(color: Colors.indigoAccent),
                            ),
                            child: Text(sched['status'], style: const TextStyle(color: Colors.indigoAccent, fontSize: 10, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(sched['title'], style: const TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 6),
                      Row(
                        children: [
                          const Icon(Icons.access_time_rounded, color: Color(0xFF94A3B8), size: 14),
                          const SizedBox(width: 4),
                          Text(sched['time'], style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
                        ],
                      ),
                    ],
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _openScheduleModal,
        backgroundColor: const Color(0xFF4F46E5),
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}
