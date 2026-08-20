export interface User {
  id: number;
  email: string;
  full_name?: string;
  target_role?: string;
  experience_level?: string;
  programming_languages?: string[];
  phone_number?: string;
  profile_picture?: string;
  auth_provider?: string;
  email_verified?: boolean;
  is_active: boolean;
}

export interface Question {
  id?: number;
  question_order: number;
  category: string;
  question_text: string;
  key_aspects: string[];
  options?: string[];
  correct_option?: string;
  explanation?: string;
}

export interface StarScore {
  situation: number;
  task: number;
  action: number;
  result: number;
}

export interface FeedbackData {
  overall_score: number;
  score?: number;
  clarity: number;
  relevance: number;
  confidence: number;
  structure: number;
  technical_depth: number;
  star_analysis?: StarScore;
  strengths: string[];
  improvements: string[];
  suggested_answer: string;
  follow_up_questions: string[];
}

export interface InterviewSession {
  id: number;
  session_id: string;
  title: string;
  mode: string; // practice, mock, coding
  role: string;
  experience_level: string;
  industry: string;
  interview_type: string;
  difficulty: string;
  overall_score: number;
  status: string;
  created_at: string;
  questions: Question[];
}

export interface ResumeIssue {
  id: string;
  type: string; // Spelling, Capitalization, Spacing, Duplicate Spaces, Grammar, Formatting
  severity: 'Critical' | 'Warning' | 'Suggestion';
  found: string;
  suggested: string;
  why: string;
  fixable: boolean;
}

export interface ResumeMetrics {
  keyword_match?: { score: number; max: number };
  structure?: { score: number; max: number };
  experience?: { score: number; max: number };
  skills?: { score: number; max: number };
  formatting?: { score: number; max: number };
  contact_info?: { score: number; max: number };
  grammar?: { score: number; max: number };
}

export interface ResumeAnalytics {
  grammar_pct?: number;
  spelling_pct?: number;
  formatting_pct?: number;
  keyword_pct?: number;
  completeness_pct?: number;
}

export interface ResumeItem {
  id: number;
  user_id?: number;
  title: string;
  filename: string;
  template_id: string;
  version_name: string;
  is_primary?: boolean;
  extracted_text?: string;
  personal_info?: {
    name?: string;
    email?: string;
    phone?: string;
    location?: string;
    target_role?: string;
    experience_level?: string;
    linkedin?: string;
    github?: string;
  };
  summary?: string;
  experience?: any[];
  education?: any[];
  skills?: string[];
  projects?: any[];
  certifications?: string[];
  achievements?: string[];
  languages?: string[];
  links?: string[];
  ats_score?: number;
  metrics?: ResumeMetrics;
  analytics?: ResumeAnalytics;
  issues?: ResumeIssue[];
  strengths?: string[];
  missing_skills?: string[];
  created_at?: string;
  updated_at?: string;
}

export interface ResumeAnalysis {
  id?: number;
  filename: string;
  skills: string[];
  experience_summary: string;
  strengths: string[];
  missing_skills: string[];
  potential_questions: string[];
  preparation_topics: string[];
  ats_score?: number;
  created_at?: string;
}

export interface JobDescriptionAnalysis {
  id?: number;
  job_title: string;
  company_name?: string;
  required_skills: string[];
  preferred_skills: string[];
  responsibilities: string[];
  keywords: string[];
  likely_interview_topics: string[];
  personalized_prep_plan: string[];
  created_at?: string;
}

export interface AppSettings {
  app_name: string;
  ai_provider: string;
  ai_model: string;
  response_style: string;
  difficulty: string;
  speech_recognition: string;
  theme: string;
  data_retention_days: number;
  api_key_configured: boolean;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
  target_role: string;
  experience_level: string;
  programming_languages: string[];
  terms_accepted: boolean;
  phone_number?: string;
  location?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}
