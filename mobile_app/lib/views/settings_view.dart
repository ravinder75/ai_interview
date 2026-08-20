import 'package:flutter/material.dart';
import '../models/app_models.dart';

class SettingsView extends StatefulWidget {
  final UserSettings userSettings;
  final Function(UserSettings settings) onSaveSettings;
  const SettingsView({
    super.key,
    required this.userSettings,
    required this.onSaveSettings,
  });

  @override
  State<SettingsView> createState() => _SettingsViewState();
}

class _SettingsViewState extends State<SettingsView> {
  late TextEditingController _nameController;
  late TextEditingController _emailController;
  late TextEditingController _phoneController;
  late TextEditingController _apiKeyController;

  late String _selectedRole;
  late String _selectedExperience;
  late String _selectedCountry;
  late String _selectedTimeZone;
  late String _selectedModel;

  final List<String> _roles = [
    'Software Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
    'Full-Stack Developer',
    'Python Developer',
    'Java Developer',
    'JavaScript Developer',
    'React Developer',
    'Vue Developer',
    'Node.js Developer',
    'Mobile Developer',
    'Android Developer',
    'iOS Developer',
    'Flutter Mobile Developer',
    'Device Management Specialist',
    'Mobile Device Management (MDM) Administrator',
    'System Administrator / Systems Engineer',
    'IT Support & Infrastructure Specialist',
    'Network Engineer',
    'Data Analyst',
    'Data Scientist',
    'Machine Learning Engineer',
    'AI Engineer',
    'DevOps Engineer',
    'Cloud Engineer',
    'Cybersecurity Engineer',
    'QA Engineer',
    'Automation Tester',
    'Database Developer',
    'SQL Developer',
    'Product Manager',
    'Project Manager',
    'Business Analyst',
    'UI/UX Designer',
    'Medical Coding Specialist',
    'Certified Professional Coder (CPC)',
    'Medical Billing & Coding Specialist',
    'Inpatient / Outpatient Coder',
    'Clinical Documentation Specialist (CDIS)',
    'Health Information Management (HIM) Specialist',
    'Medical Officer / Doctor',
    'Medical Officer / Physician',
    'General Physician',
    'Staff Nurse / Nursing Officer',
    'Pharmacist',
    'Medical Lab Technician',
    'Hospital Administrator',
    'Radiology Technician',
    'Mechanical Engineer',
    'Electrical & Electronics Engineer',
    'Civil Engineer',
    'Chemical Engineer',
    'Biomedical Engineer',
    'Automobile Engineer',
    'Aeronautical Engineer',
    'Operations Manager / Specialist',
    'Customer Support Specialist',
    'Client Success Manager',
    'Financial Analyst',
    'Chartered Accountant (CA)',
    'HR Manager / Specialist',
    'Marketing Executive / Manager',
    'Sales Operations Specialist',
    'Supply Chain & Logistics Manager',
    'Legal Advisor / Corporate Lawyer',
    'Other'
  ];

  final List<String> _experienceLevels = [
    '0-1 Years (Entry Level)',
    '1-3 Years (Junior)',
    '3-5 Years (Mid Level)',
    '5+ Years (Senior Lead)',
  ];

  final List<Map<String, String>> _countries = [
    {'name': 'India (IST +5:30)', 'code': 'IN', 'flag': '🇮🇳'},
    {'name': 'United States (EST -5:00)', 'code': 'US', 'flag': '🇺🇸'},
    {'name': 'United Kingdom (GMT +0:00)', 'code': 'UK', 'flag': '🇬🇧'},
    {'name': 'Canada (EST -5:00)', 'code': 'CA', 'flag': '🇨🇦'},
    {'name': 'Australia (AEST +10:00)', 'code': 'AU', 'flag': '🇦🇺'},
    {'name': 'Germany (CET +1:00)', 'code': 'DE', 'flag': '🇩🇪'},
    {'name': 'Singapore (SGT +8:00)', 'code': 'SG', 'flag': '🇸🇬'},
    {'name': 'United Arab Emirates (GST +4:00)', 'code': 'AE', 'flag': '🇦🇪'},
  ];

  final List<Map<String, String>> _timezones = [
    {'label': 'Asia/Kolkata (IST - Kolkata, Mumbai, Delhi)', 'value': 'Asia/Kolkata'},
    {'label': 'America/New_York (EST - New York, Washington)', 'value': 'America/New_York'},
    {'label': 'America/Los_Angeles (PST - San Francisco, Seattle)', 'value': 'America/Los_Angeles'},
    {'label': 'Europe/London (GMT - London, Manchester)', 'value': 'Europe/London'},
    {'label': 'Europe/Berlin (CET - Berlin, Frankfurt)', 'value': 'Europe/Berlin'},
    {'label': 'Asia/Singapore (SGT - Singapore)', 'value': 'Asia/Singapore'},
    {'label': 'Asia/Dubai (GST - Dubai, Abu Dhabi)', 'value': 'Asia/Dubai'},
    {'label': 'Australia/Sydney (AEST - Sydney, Melbourne)', 'value': 'Australia/Sydney'},
  ];

  final List<Map<String, String>> _availableModels = [
    {
      'label': 'Gemini 2.0 Flash Lite (Free)',
      'value': 'google/gemini-2.0-flash-lite-001:free',
    },
    {
      'label': 'Llama 3.3 70B Instruct (Free)',
      'value': 'meta-llama/llama-3.3-70b-instruct:free',
    },
    {
      'label': 'Qwen 2.5 Coder 32B (Free)',
      'value': 'qwen/qwen-2.5-coder-32b-instruct:free',
    },
    {
      'label': 'OpenAI GPT-4o Mini (Custom Key)',
      'value': 'openai/gpt-4o-mini',
    },
  ];

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.userSettings.candidateName);
    _emailController = TextEditingController(text: widget.userSettings.email);
    _phoneController = TextEditingController(text: widget.userSettings.phoneNumber);

    _selectedRole = _roles.contains(widget.userSettings.targetRole) ? widget.userSettings.targetRole : 'Full Stack Developer';
    _selectedExperience = widget.userSettings.experienceLevel;
    _selectedCountry = _countries.any((c) => c['name'] == widget.userSettings.country) ? widget.userSettings.country : 'India (IST +5:30)';
    _selectedTimeZone = _timezones.any((tz) => tz['value'] == widget.userSettings.timeZone) ? widget.userSettings.timeZone : 'Asia/Kolkata';
    _selectedModel = widget.userSettings.selectedModel;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  void _saveConfiguration() {
    final updated = widget.userSettings.copyWith(
      candidateName: _nameController.text.trim(),
      email: _emailController.text.trim(),
      phoneNumber: _phoneController.text.trim(),
      targetRole: _selectedRole,
      experienceLevel: _selectedExperience,
      country: _selectedCountry,
      timeZone: _selectedTimeZone,
      selectedModel: _selectedModel,
    );

    widget.onSaveSettings(updated);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('✓ Profile, Country & Timezone Settings Saved Successfully!'),
        backgroundColor: Colors.green,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text(
          'Profile & Preferences Settings',
          style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Candidate Profile Card
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
                  const Row(
                    children: [
                      Icon(Icons.person_rounded, color: Color(0xFF818CF8)),
                      SizedBox(width: 8),
                      Text('Candidate Profile Information', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 14),

                  const Text('Full Name', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _nameController,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: const Color(0xFF020617),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                    ),
                  ),
                  const SizedBox(height: 12),

                  const Text('Email Address', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _emailController,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: const Color(0xFF020617),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                    ),
                  ),
                  const SizedBox(height: 12),

                  const Text('Phone Number', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _phoneController,
                    style: const TextStyle(color: Colors.white, fontSize: 12),
                    decoration: InputDecoration(
                      filled: true,
                      fillColor: const Color(0xFF020617),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                    ),
                  ),
                  const SizedBox(height: 12),

                  const Text('Target Candidate Role', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(color: const Color(0xFF020617), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFF334155))),
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
                  const SizedBox(height: 12),

                  const Text('Experience Level', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(color: const Color(0xFF020617), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFF334155))),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedExperience,
                        dropdownColor: const Color(0xFF0F172A),
                        isExpanded: true,
                        items: _experienceLevels.map((e) => DropdownMenuItem(value: e, child: Text(e, style: const TextStyle(color: Colors.white, fontSize: 12)))).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedExperience = val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Country & Time Zone Selection Card
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
                  const Row(
                    children: [
                      Icon(Icons.public_rounded, color: Color(0xFF34D399)),
                      SizedBox(width: 8),
                      Text('Country & Timezone Region', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Select your country location and timezone for scheduling accurate interview reminders.',
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                  ),
                  const SizedBox(height: 14),

                  const Text('Select Country & Region', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(color: const Color(0xFF020617), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFF334155))),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedCountry,
                        dropdownColor: const Color(0xFF0F172A),
                        isExpanded: true,
                        items: _countries.map((c) {
                          return DropdownMenuItem<String>(
                            value: c['name'],
                            child: Text('${c['flag']}  ${c['name']}', style: const TextStyle(color: Colors.white, fontSize: 12)),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedCountry = val);
                        },
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  const Text('Select Time Zone', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(color: const Color(0xFF020617), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFF334155))),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedTimeZone,
                        dropdownColor: const Color(0xFF0F172A),
                        isExpanded: true,
                        items: _timezones.map((tz) {
                          return DropdownMenuItem<String>(
                            value: tz['value'],
                            child: Text(tz['label']!, style: const TextStyle(color: Colors.white, fontSize: 11)),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedTimeZone = val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // OpenRouter API Configuration Card
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
                  const Row(
                    children: [
                      Icon(Icons.smart_toy_rounded, color: Color(0xFF10B981)),
                      SizedBox(width: 8),
                      Text('AI SERVICE', style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: const Color(0xFF065F46).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFF10B981).withOpacity(0.4)),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.circle, color: Color(0xFF10B981), size: 10),
                        SizedBox(width: 8),
                        Text('● AI Connected', style: TextStyle(color: Color(0xFF34D399), fontSize: 13, fontWeight: FontWeight.bold)),
                        Spacer(),
                        Text('Global Backend Managed', style: TextStyle(color: Colors.grey, fontSize: 11)),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  const Text('Select AI Model', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(color: const Color(0xFF020617), borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFF334155))),
                    child: DropdownButtonHideUnderline(
                      child: DropdownButton<String>(
                        value: _selectedModel,
                        dropdownColor: const Color(0xFF0F172A),
                        isExpanded: true,
                        items: _availableModels.map((m) {
                          return DropdownMenuItem<String>(
                            value: m['value'],
                            child: Text(m['label']!, style: const TextStyle(color: Colors.white, fontSize: 12)),
                          );
                        }).toList(),
                        onChanged: (val) {
                          if (val != null) setState(() => _selectedModel = val);
                        },
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _saveConfiguration,
                icon: const Icon(Icons.save_rounded, size: 18),
                label: const Text('Save Profile & Settings', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
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
    );
  }
}
