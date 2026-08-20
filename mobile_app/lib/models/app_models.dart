class UserSettings {
  final String openRouterBaseUrl;
  final String selectedModel;
  final String candidateName;
  final String email;
  final String targetRole;
  final String experienceLevel;
  final String country;
  final String timeZone;
  final String phoneNumber;

  UserSettings({
    this.openRouterBaseUrl = 'https://openrouter.ai/api/v1',
    this.selectedModel = 'google/gemini-2.0-flash-lite-001:free',
    this.candidateName = 'Ravinder Nyalakanti',
    this.email = 'ravinder@example.com',
    this.targetRole = 'Full-Stack Developer',
    this.experienceLevel = '3-5 Years',
    this.country = 'India (IST +5:30)',
    this.timeZone = 'Asia/Kolkata',
    this.phoneNumber = '+91 98765 43210',
  });

  UserSettings copyWith({
    String? openRouterBaseUrl,
    String? selectedModel,
    String? candidateName,
    String? email,
    String? targetRole,
    String? experienceLevel,
    String? country,
    String? timeZone,
    String? phoneNumber,
  }) {
    return UserSettings(
      openRouterBaseUrl: openRouterBaseUrl ?? this.openRouterBaseUrl,
      selectedModel: selectedModel ?? this.selectedModel,
      candidateName: candidateName ?? this.candidateName,
      email: email ?? this.email,
      targetRole: targetRole ?? this.targetRole,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      country: country ?? this.country,
      timeZone: timeZone ?? this.timeZone,
      phoneNumber: phoneNumber ?? this.phoneNumber,
    );
  }

  Map<String, dynamic> toJson() => {
        'openRouterBaseUrl': openRouterBaseUrl,
        'selectedModel': selectedModel,
        'candidateName': candidateName,
        'email': email,
        'targetRole': targetRole,
        'experienceLevel': experienceLevel,
        'country': country,
        'timeZone': timeZone,
        'phoneNumber': phoneNumber,
      };

  factory UserSettings.fromJson(Map<String, dynamic> json) => UserSettings(
        openRouterBaseUrl: json['openRouterBaseUrl'] ?? 'https://openrouter.ai/api/v1',
        selectedModel: json['selectedModel'] ?? 'google/gemini-2.0-flash-lite-001:free',
        candidateName: json['candidateName'] ?? 'Ravinder Nyalakanti',
        email: json['email'] ?? 'ravinder@example.com',
        targetRole: json['targetRole'] ?? 'Full-Stack Developer',
        experienceLevel: json['experienceLevel'] ?? '3-5 Years',
        country: json['country'] ?? 'India (IST +5:30)',
        timeZone: json['timeZone'] ?? 'Asia/Kolkata',
        phoneNumber: json['phoneNumber'] ?? '+91 98765 43210',
      );
}

class InterviewReportModel {
  final String sessionId;
  final String candidateName;
  final String targetRole;
  final int overallScore;
  final int technicalScore;
  final int communicationScore;
  final int resumeKnowledgeScore;
  final String summary;
  final String finalRecommendation;
  final List<String> strengths;
  final List<String> weaknesses;

  InterviewReportModel({
    required this.sessionId,
    required this.candidateName,
    required this.targetRole,
    required this.overallScore,
    required this.technicalScore,
    required this.communicationScore,
    required this.resumeKnowledgeScore,
    required this.summary,
    required this.finalRecommendation,
    required this.strengths,
    required this.weaknesses,
  });

  factory InterviewReportModel.fromJson(Map<String, dynamic> json) {
    final summaryObj = json['interview_summary'] ?? {};
    return InterviewReportModel(
      sessionId: json['session_id'] ?? 'sess-live',
      candidateName: (json['candidate'] ?? {})['name'] ?? 'Candidate',
      targetRole: (json['candidate'] ?? {})['target_role'] ?? 'Software Engineer',
      overallScore: json['overall_score'] ?? summaryObj['overall_score'] ?? 0,
      technicalScore: json['technical_score'] ?? 0,
      communicationScore: json['communication_score'] ?? 0,
      resumeKnowledgeScore: json['resume_knowledge_score'] ?? 0,
      summary: summaryObj['summary'] ?? json['summary'] ?? 'Evaluation complete.',
      finalRecommendation: json['final_recommendation'] ?? 'Pass',
      strengths: List<String>.from(json['strengths'] ?? []),
      weaknesses: List<String>.from(json['weaknesses'] ?? []),
    );
  }
}
