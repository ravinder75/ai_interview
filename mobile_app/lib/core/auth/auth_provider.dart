import 'package:flutter/material.dart';
import '../../services/auth_service.dart';
import '../../models/user.dart';
import '../storage/token_storage.dart';

class AuthProvider extends ChangeNotifier {
  UserModel? _currentUser;
  bool _isLoading = true;

  UserModel? get currentUser => _currentUser;
  bool get isAuthenticated => _currentUser != null;
  bool get isLoading => _isLoading;

  AuthProvider() {
    _initAuth();
  }

  Future<void> _initAuth() async {
    _isLoading = true;
    notifyListeners();
    final token = await TokenStorage.getToken();
    if (token != null) {
      _currentUser = await AuthService.getCurrentUser();
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    notifyListeners();
    try {
      final user = await AuthService.login(email: email, password: password);
      if (user != null) {
        _currentUser = user;
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      print('Auth error: $e');
    }
    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<bool> register(String fullName, String email, String password, String targetRole) async {
    _isLoading = true;
    notifyListeners();
    try {
      final user = await AuthService.register(
        fullName: fullName,
        email: email,
        password: password,
        targetRole: targetRole,
      );
      if (user != null) {
        _currentUser = user;
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      print('Register error: $e');
    }
    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<void> logout() async {
    await AuthService.logout();
    _currentUser = null;
    notifyListeners();
  }

  void setAuthenticatedUser(Map<String, dynamic> userData) {
    _currentUser = UserModel.fromJson(userData);
    _isLoading = false;
    notifyListeners();
  }

  void updateProfile(UserModel updated) {
    _currentUser = updated;
    notifyListeners();
  }
}
