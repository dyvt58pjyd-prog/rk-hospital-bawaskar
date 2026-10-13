import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/appointment.dart';

class ApiService {
  static const String baseUrl = 'https://rk-hospital-bawaskar.onrender.com/api/v1';

  // GET /api/v1/appointments
  static Future<List<Appointment>> getAppointments() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/appointments/'),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        List<dynamic> list = data is List ? data : (data['results'] ?? data['appointments'] ?? []);
        return list.map((item) => Appointment.fromJson(item)).toList();
      } else {
        throw Exception('Failed to load appointments (Code: ${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  // POST /api/v1/appointments
  static Future<bool> createAppointment(Appointment appointment) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/appointments/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(appointment.toJson()),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      } else {
        throw Exception('Failed to book appointment (Code: ${response.statusCode}): ${response.body}');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
