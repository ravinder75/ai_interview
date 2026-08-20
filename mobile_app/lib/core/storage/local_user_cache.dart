import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LocalUserCache {
  static String _getUserKey(String userId, String keyType) => 'cache_user_${userId}_$keyType';

  static Future<void> cacheData(String userId, String keyType, dynamic data) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_getUserKey(userId, keyType), jsonEncode(data));
  }

  static Future<dynamic> getCachedData(String userId, String keyType) async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_getUserKey(userId, keyType));
    if (raw == null) return null;
    return jsonDecode(raw);
  }

  static Future<void> clearUserCache(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    final keys = prefs.getKeys().where((k) => k.startsWith('cache_user_$userId')).toList();
    for (final k in keys) {
      await prefs.remove(k);
    }
  }
}
