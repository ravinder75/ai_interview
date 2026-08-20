import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';

class LocalSyncQueue {
  static const String _queuePrefix = 'pending_offline_queue_user_';

  static Future<void> enqueueAction(String userId, String actionType, Map<String, dynamic> payload) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_queuePrefix$userId';
    final raw = prefs.getStringList(key) ?? [];

    final item = {
      'id': 'sync_${DateTime.now().millisecondsSinceEpoch}',
      'action_type': actionType,
      'payload': payload,
      'created_at': DateTime.now().toIso8601String(),
    };

    raw.add(jsonEncode(item));
    await prefs.setStringList(key, raw);
  }

  static Future<List<Map<String, dynamic>>> getPendingActions(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_queuePrefix$userId';
    final raw = prefs.getStringList(key) ?? [];

    return raw.map((str) => jsonDecode(str) as Map<String, dynamic>).toList();
  }

  static Future<void> clearUserQueue(String userId) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_queuePrefix$userId';
    await prefs.remove(key);
  }

  static Future<void> removeAction(String userId, String actionId) async {
    final prefs = await SharedPreferences.getInstance();
    final key = '$_queuePrefix$userId';
    final raw = prefs.getStringList(key) ?? [];

    final updated = raw.where((str) {
      final decoded = jsonDecode(str);
      return decoded['id'] != actionId;
    }).toList();

    await prefs.setStringList(key, updated);
  }
}
