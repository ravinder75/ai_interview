import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'core/auth/auth_provider.dart';
import 'views/dashboard_view.dart';
import 'views/mock_interview_view.dart';
import 'views/coding_interview_view.dart';
import 'views/interview_schedule_view.dart';
import 'views/resume_analyzer_view.dart';
import 'views/session_history_view.dart';
import 'views/settings_view.dart';
import 'views/chatbot_view.dart';
import 'views/practice_questions_view.dart';
import 'views/pricing_features_view.dart';
import 'views/notifications_view.dart';
import 'views/job_analysis_view.dart';
import 'views/login_view.dart';
import 'views/register_view.dart';
import 'models/app_models.dart';
import 'widgets/custom_widgets.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => AuthProvider(),
      child: const AiInterviewCoachApp(),
    ),
  );
}

class AiInterviewCoachApp extends StatelessWidget {
  const AiInterviewCoachApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AI Mock Interview Coach',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF020617),
        primaryColor: const Color(0xFF4F46E5),
      ),
      home: Consumer<AuthProvider>(
        builder: (context, auth, _) {
          if (auth.isLoading) {
            return const Scaffold(
              backgroundColor: Color(0xFF020617),
              body: Center(
                child: CircularProgressIndicator(color: Color(0xFF818CF8)),
              ),
            );
          }
          if (!auth.isAuthenticated) {
            return const AuthNavigationWrapper();
          }
          return const MainMobileNavigation();
        },
      ),
    );
  }
}

class AuthNavigationWrapper extends StatefulWidget {
  const AuthNavigationWrapper({super.key});

  @override
  State<AuthNavigationWrapper> createState() => _AuthNavigationWrapperState();
}

class _AuthNavigationWrapperState extends State<AuthNavigationWrapper> {
  bool _showRegisterView = false;

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context, listen: false);

    if (_showRegisterView) {
      return RegisterView(
        onRegisterSuccess: (userData) {
          auth.setAuthenticatedUser(userData);
        },
        onNavigateToLogin: () => setState(() => _showRegisterView = false),
      );
    }

    return LoginView(
      onLoginSuccess: (userData) {
        auth.setAuthenticatedUser(userData);
      },
      onNavigateToRegister: () => setState(() => _showRegisterView = true),
    );
  }
}

class MainMobileNavigation extends StatefulWidget {
  const MainMobileNavigation({super.key});

  @override
  State<MainMobileNavigation> createState() => _MainMobileNavigationState();
}

class _MainMobileNavigationState extends State<MainMobileNavigation> {
  int _currentIndex = 0;
  bool _isOffline = false;

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    final user = auth.currentUser;

    final userSettings = UserSettings(
      candidateName: user?.fullName ?? 'Candidate User',
      email: user?.email ?? 'candidate@example.com',
      targetRole: user?.targetRole ?? 'Full-Stack Developer',
      experienceLevel: user?.experienceLevel ?? '3-5 Years',
    );

    final List<Widget> pages = [
      MobileDashboardView(
        onNavigateToMock: () => setState(() => _currentIndex = 1),
        onNavigateToPractice: () => setState(() => _currentIndex = 8),
        onNavigateToResume: () => setState(() => _currentIndex = 4),
        onNavigateToJobAnalysis: () => setState(() => _currentIndex = 7),
      ),
      MockInterviewView(userSettings: userSettings),
      const CodingInterviewView(),
      const InterviewScheduleView(),
      const ResumeAnalyzerView(),
      const SessionHistoryView(),
      SettingsView(
        userSettings: userSettings,
        onSaveSettings: (newSettings) {},
      ),
      const MobileJobAnalysisView(),
      const PracticeQuestionsView(),
      const MobileChatBotView(),
      const NotificationsView(),
      const PricingAndFeaturesView(),
    ];

    return Scaffold(
      drawer: Drawer(
        backgroundColor: const Color(0xFF0F172A),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            UserAccountsDrawerHeader(
              decoration: const BoxDecoration(color: Color(0xFF1E1B4B)),
              accountName: Text(user?.fullName ?? 'Candidate User', style: const TextStyle(fontWeight: FontWeight.bold)),
              accountEmail: Text(user?.email ?? 'candidate@example.com', style: const TextStyle(color: Color(0xFF94A3B8))),
              currentAccountPicture: const CircleAvatar(
                backgroundColor: Color(0xFF4F46E5),
                child: Icon(Icons.person_rounded, color: Colors.white, size: 32),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.dashboard_rounded, color: Color(0xFF818CF8)),
              title: const Text('Dashboard & Overview', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 0);
              },
            ),
            ListTile(
              leading: const Icon(Icons.video_call_rounded, color: Color(0xFF818CF8)),
              title: const Text('Live AI Mock Room', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 1);
              },
            ),
            ListTile(
              leading: const Icon(Icons.code_rounded, color: Color(0xFF818CF8)),
              title: const Text('Coding Arena (DSA & InterviewBit)', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 2);
              },
            ),
            ListTile(
              leading: const Icon(Icons.work_rounded, color: Color(0xFF818CF8)),
              title: const Text('Job Analysis & Live Matches', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 7);
              },
            ),
            ListTile(
              leading: const Icon(Icons.chat_bubble_rounded, color: Color(0xFF818CF8)),
              title: const Text('AI Career Chatbot', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 9);
              },
            ),
            ListTile(
              leading: const Icon(Icons.quiz_rounded, color: Color(0xFF818CF8)),
              title: const Text('Practice Questions Bank', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 8);
              },
            ),
            ListTile(
              leading: const Icon(Icons.calendar_month_rounded, color: Color(0xFF818CF8)),
              title: const Text('Interview Schedule', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 3);
              },
            ),
            ListTile(
              leading: const Icon(Icons.description_rounded, color: Color(0xFF818CF8)),
              title: const Text('Resume AI Analyzer', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 4);
              },
            ),
            ListTile(
              leading: const Icon(Icons.history_rounded, color: Color(0xFF818CF8)),
              title: const Text('Session Evaluation History', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 5);
              },
            ),
            ListTile(
              leading: const Icon(Icons.notifications_active_rounded, color: Color(0xFF818CF8)),
              title: const Text('Notifications', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 10);
              },
            ),
            ListTile(
              leading: const Icon(Icons.workspace_premium_rounded, color: Colors.amber),
              title: const Text('Plans, Features & About', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 11);
              },
            ),
            ListTile(
              leading: const Icon(Icons.settings_rounded, color: Color(0xFF818CF8)),
              title: const Text('Profile & Settings', style: TextStyle(color: Colors.white)),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 6);
              },
            ),
            const Divider(color: Color(0xFF1E293B)),
            ListTile(
              leading: const Icon(Icons.logout_rounded, color: Colors.redAccent),
              title: const Text('Sign Out', style: TextStyle(color: Colors.redAccent)),
              onTap: () async {
                Navigator.pop(context);
                await auth.logout();
              },
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            NetworkOfflineBanner(isOffline: _isOffline),
            Expanded(child: pages[_currentIndex]),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex > 5 ? 0 : _currentIndex,
        backgroundColor: const Color(0xFF0F172A),
        selectedItemColor: const Color(0xFF818CF8),
        unselectedItemColor: const Color(0xFF64748B),
        type: BottomNavigationBarType.fixed,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_rounded),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.video_call_rounded),
            label: 'Live Room',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.code_rounded),
            label: 'Coding',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_month_rounded),
            label: 'Schedule',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.description_rounded),
            label: 'Resume',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.history_rounded),
            label: 'History',
          ),
        ],
      ),
    );
  }
}
