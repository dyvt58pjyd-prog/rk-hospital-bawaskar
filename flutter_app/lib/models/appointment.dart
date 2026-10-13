class Appointment {
  final int? id;
  final String patientName;
  final String date;
  final String procedure;
  final String? status;

  Appointment({
    this.id,
    required this.patientName,
    required this.date,
    required this.procedure,
    this.status,
  });

  factory Appointment.fromJson(Map<String, dynamic> json) {
    return Appointment(
      id: json['id'],
      patientName: json['patient_name'] ?? json['patientName'] ?? 'Unknown Patient',
      date: json['date'] ?? json['appointment_date'] ?? '',
      procedure: json['procedure'] ?? json['treatment'] ?? 'General Consultation',
      status: json['status'] ?? 'Scheduled',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'patient_name': patientName,
      'date': date,
      'procedure': procedure,
    };
  }
}
