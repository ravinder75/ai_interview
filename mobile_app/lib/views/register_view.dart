import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../core/errors/api_exception.dart';

class RegisterView extends StatefulWidget {
  final Function(Map<String, dynamic> userData) onRegisterSuccess;
  final VoidCallback onNavigateToLogin;

  const RegisterView({
    super.key,
    required this.onRegisterSuccess,
    required this.onNavigateToLogin,
  });

  @override
  State<RegisterView> createState() => _RegisterViewState();
}

class _RegisterViewState extends State<RegisterView> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  String _selectedCountry = 'IN';
  String _selectedRole = 'Software Engineer';
  String _selectedExperience = '3-5 Years';
  final List<String> _selectedLanguages = [];
  bool _termsAccepted = false;
  bool _isLoading = false;

  final List<Map<String, String>> _countries = [
    {'code': 'IN', 'label': 'India (+5:30 IST)'},
    {'code': 'US', 'label': 'United States (EST/PST)'},
    {'code': 'GB', 'label': 'United Kingdom (GMT/BST)'},
    {'code': 'AE', 'label': 'United Arab Emirates (GST)'},
    {'code': 'SG', 'label': 'Singapore (SGT)'},
    {'code': 'AU', 'label': 'Australia (AEST)'},
    {'code': 'CA', 'label': 'Canada (EST/PST)'},
    {'code': 'DE', 'label': 'Germany (CET)'},
  ];

  final List<String> _roles = [
    // IT, Infrastructure & Systems Engineering
    'Software Engineer',
    'Frontend Developer',
    'Backend Developer',
    'Full Stack Developer',
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
    
    // Medical, Healthcare & Medical Coding Branches
    'Medical Coding Specialist',
    'Certified Professional Coder (CPC)',
    'Medical Billing & Coding Specialist',
    'Inpatient / Outpatient Coder',
    'Clinical Documentation Specialist (CDIS)',
    'Health Information Management (HIM) Specialist',
    'Medical Officer / Doctor',
    'General Physician',
    'Staff Nurse / Nursing Officer',
    'Pharmacist',
    'Medical Lab Technician',
    'Hospital Administrator',
    'Radiology Technician',
    
    // Core Engineering & Technical Branches
    'Mechanical Engineer',
    'Electrical & Electronics Engineer',
    'Civil Engineer',
    'Chemical Engineer',
    'Biomedical Engineer',
    'Automobile Engineer',
    'Aeronautical Engineer',
    
    // Business, Operations, Finance & Management
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

  final List<String> _experiences = [
    'Fresher',
    '0-1 Years',
    '1-3 Years',
    '3-5 Years',
    '5-8 Years',
    '8+ Years',
  ];

  final List<String> _availableLanguages = [
    'Python',
    'JavaScript',
    'TypeScript',
    'Java',
    'C++',
    'Dart / Flutter',
    'Go',
    'Rust',
    'SQL',
  ];

  void _handleRegister() async {
    final name = _nameController.text.trim();
    final email = _emailController.text.trim().toLowerCase();
    final password = _passwordController.text;
    final confirmPassword = _confirmPasswordController.text;

    if (name.isEmpty) {
      _showError('Please enter your full name.');
      return;
    }
    if (email.isEmpty || !email.contains('@')) {
      _showError('Please enter a valid email address.');
      return;
    }
    if (password.length < 8) {
      _showError('Password must contain at least 8 characters.');
      return;
    }
    if (!RegExp(r'[A-Z]').hasMatch(password) ||
        !RegExp(r'[a-z]').hasMatch(password) ||
        !RegExp(r'\d').hasMatch(password) ||
        !RegExp(r'[!@#$%^&*()_+\-=\[\]{};' ':' r'"\\|,.<>\/?~`]').hasMatch(password)) {
      _showError('Password requires uppercase, lowercase, number, and special character (e.g. Pass123!).');
      return;
    }
    if (password != confirmPassword) {
      _showError('Passwords do not match.');
      return;
    }
    if (!_termsAccepted) {
      _showError('Please accept the Terms and Privacy Policy.');
      return;
    }

    setState(() => _isLoading = true);

    try {
      final userData = await ApiService.registerUser(
        name: name,
        email: email,
        password: password,
        role: _selectedRole,
        experienceLevel: _selectedExperience,
        programmingLanguages: _selectedLanguages,
        termsAccepted: _termsAccepted,
      );

      setState(() => _isLoading = false);

      if (userData != null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('✓ Account created successfully! Welcome.'),
              backgroundColor: Colors.green,
            ),
          );
          widget.onRegisterSuccess(userData);
        }
      }
    } on ApiException catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        _showError('❌ ${e.message}');
      }
    } catch (_) {
      setState(() => _isLoading = false);
      if (mounted) {
        _showError('❌ Registration failed. Email may already be registered or network is unavailable.');
      }
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: const Color(0xFF991B1B),
      ),
    );
  }

  void _handleGoogleLogin() {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('🌐 Connecting to Google OAuth backend identity...'),
        backgroundColor: Color(0xFF4F46E5),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF020617),
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 32),
          child: Container(
            constraints: const BoxConstraints(maxWidth: 440),
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: const Color(0xFF1E293B)),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF6366F1).withValues(alpha: 0.15),
                  blurRadius: 24,
                  spreadRadius: 2,
                )
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Center(
                  child: Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: const Color(0xFF4F46E5),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(Icons.person_add_rounded, color: Colors.white, size: 26),
                  ),
                ),
                const SizedBox(height: 14),
                const Center(
                  child: Text(
                    'Create your account',
                    style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(height: 4),
                const Center(
                  child: Text(
                    'Join Interview Coach AI to build interview confidence',
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 20),

                // Google OAuth Button
                SizedBox(
                  width: double.infinity,
                  height: 44,
                  child: OutlinedButton.icon(
                    onPressed: _handleGoogleLogin,
                    icon: Image.network('https://upload.wikimedia.org/wikipedia/commons/5/53/Google_%22G%22_Logo.svg', width: 18, height: 18, errorBuilder: (_, __, ___) => const Icon(Icons.g_mobiledata, color: Colors.white)),
                    label: const Text('Continue with Google', style: TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.w600)),
                    style: OutlinedButton.styleFrom(
                      backgroundColor: const Color(0xFF020617),
                      side: const BorderSide(color: Color(0xFF334155)),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                  ),
                ),

                const SizedBox(height: 16),
                Row(
                  children: [
                    const Expanded(child: Divider(color: Color(0xFF1E293B))),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 10),
                      child: Text('OR', style: TextStyle(color: Colors.grey.shade500, fontSize: 10, fontWeight: FontWeight.bold)),
                    ),
                    const Expanded(child: Divider(color: Color(0xFF1E293B))),
                  ],
                ),
                const SizedBox(height: 16),

                // Full Name
                const Text('Full Name', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: _nameController,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: InputDecoration(
                    hintText: 'Enter your full name',
                    hintStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                    filled: true,
                    fillColor: const Color(0xFF020617),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                  ),
                ),
                const SizedBox(height: 14),

                // Email
                const Text('Email', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: _emailController,
                  keyboardType: TextInputType.emailAddress,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: InputDecoration(
                    hintText: 'you@example.com',
                    hintStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                    filled: true,
                    fillColor: const Color(0xFF020617),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                  ),
                ),
                const SizedBox(height: 14),

                // Password
                const Text('Password', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: _passwordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: InputDecoration(
                    hintText: 'Create a password',
                    hintStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                    filled: true,
                    fillColor: const Color(0xFF020617),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                  ),
                ),
                const SizedBox(height: 14),

                // Confirm Password
                const Text('Confirm Password', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: _confirmPasswordController,
                  obscureText: true,
                  style: const TextStyle(color: Colors.white, fontSize: 12),
                  decoration: InputDecoration(
                    hintText: 'Re-enter your password',
                    hintStyle: const TextStyle(color: Colors.grey, fontSize: 12),
                    filled: true,
                    fillColor: const Color(0xFF020617),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: const BorderSide(color: Color(0xFF334155))),
                  ),
                ),
                const SizedBox(height: 14),

                // Country Selection
                const Text('Country', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
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
                      value: _selectedCountry,
                      dropdownColor: const Color(0xFF0F172A),
                      isExpanded: true,
                      items: _countries.map((c) => DropdownMenuItem(value: c['code'], child: Text(c['label']!, style: const TextStyle(color: Colors.white, fontSize: 12)))).toList(),
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedCountry = val);
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 14),

                // Target Role
                const Text('Target Role', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
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
                const SizedBox(height: 14),

                // Experience Level
                const Text('Experience Level', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
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
                      value: _selectedExperience,
                      dropdownColor: const Color(0xFF0F172A),
                      isExpanded: true,
                      items: _experiences.map((e) => DropdownMenuItem(value: e, child: Text(e, style: const TextStyle(color: Colors.white, fontSize: 12)))).toList(),
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedExperience = val);
                      },
                    ),
                  ),
                ),
                const SizedBox(height: 14),

                // Preferred Programming Languages
                const Text('Preferred Programming Languages', style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(
                  spacing: 6,
                  runSpacing: 6,
                  children: _availableLanguages.map((lang) {
                    final isSelected = _selectedLanguages.contains(lang);
                    return FilterChip(
                      selected: isSelected,
                      label: Text(lang, style: TextStyle(color: isSelected ? Colors.white : const Color(0xFF94A3B8), fontSize: 11)),
                      backgroundColor: const Color(0xFF020617),
                      selectedColor: const Color(0xFF4F46E5),
                      checkmarkColor: Colors.white,
                      onSelected: (selected) {
                        setState(() {
                          if (selected) {
                            _selectedLanguages.add(lang);
                          } else {
                            _selectedLanguages.remove(lang);
                          }
                        });
                      },
                    );
                  }).toList(),
                ),
                const SizedBox(height: 16),

                // Terms & Privacy Checkbox
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    SizedBox(
                      width: 24,
                      height: 24,
                      child: Checkbox(
                        value: _termsAccepted,
                        activeColor: const Color(0xFF4F46E5),
                        onChanged: (val) => setState(() => _termsAccepted = val ?? false),
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        'I agree to the Terms and Privacy Policy',
                        style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // Create Account Button
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _handleRegister,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF4F46E5),
                      foregroundColor: Colors.white,
                      elevation: 4,
                      shadowColor: const Color(0xFF4F46E5).withValues(alpha: 0.5),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: _isLoading
                        ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Text('Create Account', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  ),
                ),
                const SizedBox(height: 16),

                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('Already have an account? ', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
                    GestureDetector(
                      onTap: widget.onNavigateToLogin,
                      child: const Text('Login', style: TextStyle(color: Color(0xFF818CF8), fontSize: 12, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

