import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/api/api_config.dart';
import '../core/storage/token_storage.dart';
import '../core/errors/api_exception.dart';
import '../models/app_models.dart';

class ApiService {
  static Future<Map<String, String>> _getHeaders() async {
    final token = await TokenStorage.getToken();
    final headers = Map<String, String>.from(ApiConfig.headers);
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }
  static Future<dynamic> get(String endpoint) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .get(Uri.parse('${ApiConfig.baseUrl}$endpoint'), headers: headers)
          .timeout(const Duration(seconds: 15));
      return _processResponse(response);
    } catch (e) {
      throw ApiException('Network error or connection timeout: $e');
    }
  }

  static Future<dynamic> post(String endpoint, Map<String, dynamic> body) async {
    try {
      final headers = await _getHeaders();
      final response = await http
          .post(
            Uri.parse('${ApiConfig.baseUrl}$endpoint'),
            headers: headers,
            body: jsonEncode(body),
          )
          .timeout(const Duration(seconds: 20));
      return _processResponse(response);
    } catch (e) {
      throw ApiException('Network error or connection timeout: $e');
    }
  }

  // Candidate Login API returning complete user profile
  static Future<Map<String, dynamic>?> loginUser({required String email, required String password}) async {
    try {
      final res = await post('/auth/login', {'email': email, 'password': password});
      if (res != null) {
        if (res['access_token'] != null) {
          await TokenStorage.saveToken(res['access_token']);
        }
        return res['user'] as Map<String, dynamic>? ?? {
          'full_name': 'Candidate User',
          'email': email,
          'target_role': 'Full-Stack Developer',
        };
      }
      return null;
    } on ApiException catch (e) {
      print('Login API Error: ${e.message}');
      rethrow;
    } catch (e) {
      return null;
    }
  }

  // Candidate Registration API returning complete user profile
  static Future<Map<String, dynamic>?> registerUser({
    required String name,
    required String email,
    required String password,
    required String role,
    String experienceLevel = '3-5 Years',
    List<String> programmingLanguages = const [],
    bool termsAccepted = true,
  }) async {
    try {
      final res = await post('/auth/register', {
        'name': name,
        'email': email,
        'password': password,
        'target_role': role,
        'experience_level': experienceLevel,
        'programming_languages': programmingLanguages,
        'terms_accepted': termsAccepted,
      });
      if (res != null) {
        if (res['access_token'] != null) {
          await TokenStorage.saveToken(res['access_token']);
        }
        return res['user'] as Map<String, dynamic>? ?? {
          'full_name': name,
          'email': email,
          'target_role': role,
          'experience_level': experienceLevel,
          'programming_languages': programmingLanguages,
        };
      }
      return null;
    } on ApiException catch (e) {
      print('Registration API Error: ${e.message}');
      rethrow;
    } catch (e) {
      return null;
    }
  }

  // Create new live interview session
  static Future<Map<String, dynamic>?> createInterviewSession({
    required String role,
    required String experienceLevel,
    required String candidateName,
  }) async {
    try {
      final res = await post('/interviews/session', {
        'role': role,
        'experience_level': experienceLevel,
        'candidate_profile': {
          'name': candidateName,
          'target_role': role,
        }
      });
      return res;
    } catch (e) {
      print('Error creating interview session: $e');
      return null;
    }
  }

  static dynamic _processResponse(http.Response response) {
    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else if (response.statusCode == 401) {
      TokenStorage.clearAuth();
      throw ApiException('401 Unauthorized session expired. Please sign in again.', 401);
    } else if (response.statusCode == 403) {
      throw ApiException('403 Access denied to requested data.', 403);
    } else {
      String errorMessage = 'Server error (${response.statusCode})';
      try {
        final decoded = jsonDecode(response.body);
        if (decoded is Map && decoded['detail'] != null) {
          errorMessage = decoded['detail'].toString();
        }
      } catch (_) {}
      throw ApiException(errorMessage, response.statusCode);
    }
  }
}
