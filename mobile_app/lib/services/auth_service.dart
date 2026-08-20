import 'dart:convert';
import 'api_service.dart';
import '../core/storage/token_storage.dart';
import '../models/user.dart';

class AuthService {
  static Future<UserModel?> login({required String email, required String password}) async {
    final res = await ApiService.post('/auth/login', {
      'email': email,
      'password': password,
    });

    if (res != null && res['access_token'] != null) {
      await TokenStorage.saveToken(res['access_token']);
      final user = UserModel.fromJson(res['user'] ?? {});
      await TokenStorage.saveUserProfile(jsonEncode(user.toJson()));
      return user;
    }
    return null;
  }

  static Future<UserModel?> register({
    required String fullName,
    required String email,
    required String password,
    required String targetRole,
  }) async {
    final res = await ApiService.post('/auth/register', {
      'full_name': fullName,
      'email': email,
      'password': password,
      'target_role': targetRole,
    });

    if (res != null && res['access_token'] != null) {
      await TokenStorage.saveToken(res['access_token']);
      final user = UserModel.fromJson(res['user'] ?? {});
      await TokenStorage.saveUserProfile(jsonEncode(user.toJson()));
      return user;
    }
    return null;
  }

  static Future<UserModel?> getCurrentUser() async {
    try {
      final res = await ApiService.get('/auth/me');
      if (res != null) {
        final user = UserModel.fromJson(res);
        await TokenStorage.saveUserProfile(jsonEncode(user.toJson()));
        return user;
      }
    } catch (_) {}

    // Local cached fallback
    final cached = await TokenStorage.getUserProfile();
    if (cached != null) {
      return UserModel.fromJson(jsonDecode(cached));
    }
    return null;
  }

  static Future<void> logout() async {
    try {
      await ApiService.post('/auth/logout', {});
    } catch (_) {}
    await TokenStorage.clearAuth();
  }
}
