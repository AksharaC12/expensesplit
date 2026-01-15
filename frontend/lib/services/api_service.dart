import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ApiService {
  /// ✅ FIXED:
  /// Web → 127.0.0.1 (NOT localhost)
  /// Android Emulator → 10.0.2.2
  static const String baseUrl =
      kIsWeb ? "http://127.0.0.1:5000" : "http://10.0.2.2:5000";

  static int? userId;

  static const Duration timeout = Duration(seconds: 10);

  // ================= LOGIN =================
  static Future<Map<String, dynamic>> login(String email, String pin) async {
    try {
      final res = await http
          .post(
            Uri.parse("$baseUrl/login"),
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "email": email,
              "pin": pin,
            }),
          )
          .timeout(timeout);

      final data = jsonDecode(res.body);

      if (res.statusCode == 200) {
        userId = data["user"]["id"];
        return data;
      } else {
        throw Exception(data["error"] ?? "Invalid email or PIN");
      }
    } catch (e) {
      throw Exception("Unable to login. $e");
    }
  }

  // ================= SIGNUP =================
  static Future<void> signup(String name, String email, String pin) async {
    try {
      final res = await http
          .post(
            Uri.parse("$baseUrl/signup"),
            headers: {"Content-Type": "application/json"},
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
    } catch (e) {
      throw Exception("Signup failed. $e");
    }
  }

  // ================= CREATE GROUP =================
  static Future<void> createGroup(String name) async {
    if (userId == null) {
      throw Exception("User not logged in");
    }

    try {
      final res = await http
          .post(
            Uri.parse("$baseUrl/groups"),
            headers: {"Content-Type": "application/json"},
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
    } catch (e) {
      throw Exception("Create group failed. $e");
    }
  }

  // ================= GET GROUPS =================
  static Future<List<dynamic>> getGroups() async {
    if (userId == null) return [];

    try {
      final res =
          await http.get(Uri.parse("$baseUrl/groups/$userId")).timeout(timeout);

      if (res.statusCode == 200) {
        return jsonDecode(res.body) as List<dynamic>;
      } else {
        throw Exception("Failed to load groups");
      }
    } catch (e) {
      throw Exception("Unable to fetch groups. $e");
    }
  }

  // ================= ADD EXPENSE =================
  static Future<void> addExpense({
    required int groupId,
    required String description,
    required double amount,
  }) async {
    if (userId == null) {
      throw Exception("User not logged in");
    }

    try {
      final res = await http
          .post(
            Uri.parse("$baseUrl/expenses"),
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "group_id": groupId,
              "description": description,
              "amount": amount,
              "paid_by": userId,
            }),
          )
          .timeout(timeout);

      if (res.statusCode != 200 && res.statusCode != 201) {
        final data = jsonDecode(res.body);
        throw Exception(data["error"] ?? "Failed to add expense");
      }
    } catch (e) {
      throw Exception("Add expense failed. $e");
    }
  }

  // ================= GET BALANCES =================
  static Future<Map<String, dynamic>> getBalances(int groupId) async {
    try {
      final res = await http
          .get(Uri.parse("$baseUrl/settlements/$groupId"))
          .timeout(timeout);

      if (res.statusCode == 200) {
        return jsonDecode(res.body) as Map<String, dynamic>;
      } else {
        throw Exception("Failed to load balances");
      }
    } catch (e) {
      throw Exception("Unable to load balances. $e");
    }
  }

  // ================= SETTLE GROUP =================
  static Future<void> settleGroup(int groupId) async {
    try {
      final res = await http
          .post(
            Uri.parse("$baseUrl/settle"),
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({"group_id": groupId}),
          )
          .timeout(timeout);

      if (res.statusCode != 200) {
        final data = jsonDecode(res.body);
        throw Exception(data["error"] ?? "Settlement failed");
      }
    } catch (e) {
      throw Exception("Settlement failed. $e");
    }
  }
}
