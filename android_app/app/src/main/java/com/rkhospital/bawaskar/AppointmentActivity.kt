package com.rkhospital.bawaskar

import android.app.DatePickerDialog
import android.app.TimePickerDialog
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONArray
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*
import kotlin.concurrent.thread

class AppointmentActivity : AppCompatActivity() {

    private lateinit var listViewAppointments: ListView
    private lateinit var progressBarAppointments: ProgressBar
    private lateinit var tvEmptyAppointments: TextView
    private lateinit var btnNewAppointment: Button

    private val apiUrl = "https://rk-hospital-bawaskar.onrender.com/api/v1/appointments/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_appointment)

        listViewAppointments = findViewById(R.id.listViewAppointments)
        progressBarAppointments = findViewById(R.id.progressBarAppointments)
        tvEmptyAppointments = findViewById(R.id.tvEmptyAppointments)
        btnNewAppointment = findViewById(R.id.btnNewAppointment)

        btnNewAppointment.setOnClickListener {
            showBookingDialog()
        }

        fetchAppointments()
    }

    private fun fetchAppointments() {
        progressBarAppointments.visibility = View.VISIBLE
        tvEmptyAppointments.visibility = View.GONE

        thread {
            try {
                val url = URL(apiUrl)
                val conn = url.openConnection() as HttpURLConnection
                conn.requestMethod = "GET"
                conn.setRequestProperty("Content-Type", "application/json")

                val responseCode = conn.responseCode
                if (responseCode == HttpURLConnection.HTTP_OK) {
                    val reader = BufferedReader(InputStreamReader(conn.inputStream))
                    val response = StringBuilder()
                    var line: String?
                    while (reader.readLine().also { line = it } != null) {
                        response.append(line)
                    }
                    reader.close()

                    val jsonStr = response.toString()
                    val appointmentsList = mutableListOf<String>()

                    // Handle JSONArray or JSONObj with results
                    val jsonArray = if (jsonStr.trim().startsWith("[")) {
                        JSONArray(jsonStr)
                    } else {
                        val obj = JSONObject(jsonStr)
                        obj.optJSONArray("results") ?: obj.optJSONArray("appointments") ?: JSONArray()
                    }

                    for (i in 0 until jsonArray.length()) {
                        val obj = jsonArray.getJSONObject(i)
                        val patient = obj.optString("patient_name", obj.optString("patientName", "Patient"))
                        val procedure = obj.optString("procedure", obj.optString("treatment", "Consultation"))
                        val date = obj.optString("date", obj.optString("appointment_date", ""))
                        appointmentsList.add("🦷 $procedure\n👤 Patient: $patient\n📅 Date: $date")
                    }

                    runOnUiThread {
                        progressBarAppointments.visibility = View.GONE
                        if (appointmentsList.isEmpty()) {
                            tvEmptyAppointments.visibility = View.VISIBLE
                        } else {
                            val adapter = ArrayAdapter(
                                this,
                                android.R.layout.simple_list_item_1,
                                appointmentsList
                            )
                            listViewAppointments.adapter = adapter
                        }
                    }
                } else {
                    runOnUiThread {
                        progressBarAppointments.visibility = View.GONE
                        tvEmptyAppointments.visibility = View.VISIBLE
                        tvEmptyAppointments.text = "Failed to load appointments (Code: $responseCode)"
                    }
                }
            } catch (e: Exception) {
                runOnUiThread {
                    progressBarAppointments.visibility = View.GONE
                    tvEmptyAppointments.visibility = View.VISIBLE
                    tvEmptyAppointments.text = "Connection Error: ${e.localizedMessage}"
                }
            }
        }
    }

    private fun showBookingDialog() {
        val dialogView = layoutInflater.inflate(R.layout.dialog_book_appointment, null)
        val etPatientName = dialogView.findViewById<EditText>(R.id.etPatientName)
        val etProcedure = dialogView.findViewById<EditText>(R.id.etProcedure)
        val etDateTime = dialogView.findViewById<EditText>(R.id.etDateTime)
        val btnCancel = dialogView.findViewById<Button>(R.id.btnCancelBooking)
        val btnSubmit = dialogView.findViewById<Button>(R.id.btnSubmitBooking)

        val calendar = Calendar.getInstance()
        etDateTime.setOnClickListener {
            DatePickerDialog(
                this,
                { _, year, month, day ->
                    TimePickerDialog(
                        this,
                        { _, hour, minute ->
                            calendar.set(year, month, day, hour, minute)
                            val sdf = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
                            etDateTime.setText(sdf.format(calendar.time))
                        },
                        calendar.get(Calendar.HOUR_OF_DAY),
                        calendar.get(Calendar.MINUTE),
                        true
                    ).show()
                },
                calendar.get(Calendar.YEAR),
                calendar.get(Calendar.MONTH),
                calendar.get(Calendar.DAY_OF_MONTH)
            ).show()
        }

        val dialog = AlertDialog.Builder(this)
            .setView(dialogView)
            .create()

        btnCancel.setOnClickListener { dialog.dismiss() }

        btnSubmit.setOnClickListener {
            val name = etPatientName.text.toString().trim()
            val procedure = etProcedure.text.toString().trim()
            val dateTime = etDateTime.text.toString().trim()

            if (name.isEmpty() || procedure.isEmpty() || dateTime.isEmpty()) {
                Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            btnSubmit.isEnabled = false
            thread {
                try {
                    val url = URL(apiUrl)
                    val conn = url.openConnection() as HttpURLConnection
                    conn.requestMethod = "POST"
                    conn.setRequestProperty("Content-Type", "application/json")
                    conn.doOutput = true

                    val jsonParam = JSONObject().apply {
                        put("patient_name", name)
                        put("procedure", procedure)
                        put("date", dateTime)
                    }

                    val os = conn.outputStream
                    os.write(jsonParam.toString().toByteArray(Charsets.UTF_8))
                    os.flush()
                    os.close()

                    val responseCode = conn.responseCode
                    runOnUiThread {
                        btnSubmit.isEnabled = true
                        if (responseCode == HttpURLConnection.HTTP_OK || responseCode == HttpURLConnection.HTTP_CREATED) {
                            Toast.makeText(this, "Appointment Booked Successfully!", Toast.LENGTH_SHORT).show()
                            dialog.dismiss()
                            fetchAppointments()
                        } else {
                            Toast.makeText(this, "Failed to book (Code: $responseCode)", Toast.LENGTH_SHORT).show()
                        }
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        btnSubmit.isEnabled = true
                        Toast.makeText(this, "Error: ${e.localizedMessage}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        }

        dialog.show()
    }
}
