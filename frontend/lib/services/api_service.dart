import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  /// 🌐 Web → 127.0.0.1
  /// 📱 Android Emulator → 10.0.2.2
  static String get baseUrl {
    return kIsWeb ? "http://127.0.0.1:5000" : "http://10.0.2.2:5000";
  }

  static int? userId;
  static const Duration timeout = Duration(seconds: 10);

  static Map<String, String> get _headers => {
        "Content-Type": "application/json",
      };

  // ================= LOGIN =================
  static Future<void> login(String email, String pin) async {
    final res = await http
        .post(
          Uri.parse("$baseUrl/login"),
          headers: _headers,
          body: jsonEncode({
            "email": email,
            "pin": pin,
          }),
        )
        .timeout(timeout);

    final data = jsonDecode(res.body);

    if (res.statusCode == 200 && data["user_id"] != null) {
      userId = data["user_id"];
    } else {
      throw Exception(data["error"] ?? "Invalid email or PIN");
    }
  }

  // ================= SIGNUP =================
  static Future<void> signup(String name, String email, String pin) async {
    final res = await http
        .post(
          Uri.parse("$baseUrl/signup"),
          headers: _headers,
          body: jsonEncode({
            "name": name,
            "email": email,
            "pin": pin,
          }),
        )
        .timeout(timeout);

    if (res.statusCode != 200 && res.statusCode != 201) {
      final data = jsonDecode(res.body);
      throw Exception(data["error"] ?? "Signup failed");
    }
  }

  // ================= CREATE GROUP =================
  static Future<void> createGroup(String name) async {
    if (userId == null) throw Exception("User not logged in");

    final res = await http
        .post(
          Uri.parse("$baseUrl/groups"),
          headers: _headers,
          body: jsonEncode({
            "name": name,
            "user_id": userId,
          }),
        )
        .timeout(timeout);

    if (res.statusCode != 200 && res.statusCode != 201) {
      final data = jsonDecode(res.body);
      throw Exception(data["error"] ?? "Failed to create group");
    }
  }

  // ================= GET GROUPS =================
  static Future<List<dynamic>> getGroups() async {
    if (userId == null) return [];

    final res = await http
        .get(
          Uri.parse("$baseUrl/groups/$userId"),
          headers: _headers,
        )
        .timeout(timeout);

    if (res.statusCode == 200) {
      return jsonDecode(res.body) as List<dynamic>;
    } else {
      throw Exception("Failed to load groups");
    }
  }

  // ================= GET GROUP MEMBERS =================
  static Future<List<dynamic>> getGroupMembers(int groupId) async {
    final res = await http
        .get(
          Uri.parse("$baseUrl/groups/$groupId/members"),
          headers: _headers,
        )
        .timeout(timeout);

    if (res.statusCode == 200) {
      return jsonDecode(res.body) as List<dynamic>;
    } else {
      throw Exception(
        "Failed to load members (${res.statusCode}): ${res.body}",
      );
    }
  }

  // ================= ADD MEMBER =================
  static Future<void> addMemberByEmail(int groupId, String email) async {
    final res = await http
        .post(
          Uri.parse("$baseUrl/groups/add-member"),
          headers: _headers,
          body: jsonEncode({
            "group_id": groupId,
            "email": email,
          }),
        )
        .timeout(timeout);

    if (res.statusCode != 200 && res.statusCode != 201) {
      final data = jsonDecode(res.body);
      throw Exception(data["error"] ?? "Failed to add member");
    }
  }

  // ================= ADD EXPENSE =================
  static Future<void> addExpense({
    required int groupId,
    required String description,
    required double amount,
  }) async {
    if (userId == null) throw Exception("User not logged in");

    final res = await http
        .post(
          Uri.parse("$baseUrl/expenses"),
          headers: _headers,
          body: jsonEncode({
            "group_id": groupId,
            "paid_by": userId,
            "amount": amount,
            "description": description,
          }),
        )
        .timeout(timeout);

    if (res.statusCode != 200 && res.statusCode != 201) {
      final data = jsonDecode(res.body);
      throw Exception(data["error"] ?? "Failed to add expense");
    }
  }

  // ================= GET BALANCES =================
  static Future<List<Map<String, dynamic>>> getBalances(int groupId) async {
    final res = await http
        .get(
          Uri.parse("$baseUrl/settlements/$groupId"),
          headers: _headers,
        )
        .timeout(timeout);

    if (res.statusCode == 200) {
      return List<Map<String, dynamic>>.from(jsonDecode(res.body));
    } else {
      throw Exception("Failed to load balances");
    }
  }
}
