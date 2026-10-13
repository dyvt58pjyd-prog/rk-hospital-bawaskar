from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Patient, DentalOperatory, Appointment, ToothRecord,
    ClinicalVisit, ProcedureCatalog, TreatmentItem, DentalLabOrder,
    DentalRadiograph, Prescription, PrescriptionItem, Invoice,
    InvoiceItem, Payment, DentalMaterialInventory
)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Hospital Role & Details', {'fields': ('role', 'phone_number', 'specialization', 'qualification', 'license_number', 'avatar')}),
    )
    list_display = ['username', 'email', 'get_full_name', 'role', 'specialization', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_active']


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['mrn', 'full_name', 'phone', 'gender', 'blood_group', 'created_at']
    search_fields = ['mrn', 'first_name', 'last_name', 'phone']
    list_filter = ['gender', 'blood_group', 'has_diabetes', 'has_hypertension', 'has_allergies']


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'dentist', 'chair', 'appointment_date', 'start_time', 'status']
    list_filter = ['status', 'appointment_date', 'chair']


@admin.register(ToothRecord)
class ToothRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'tooth_number', 'status', 'surfaces_display', 'pocket_depth_mm', 'mobility', 'updated_at']
    list_filter = ['status', 'tooth_number']
    search_fields = ['patient__first_name', 'patient__last_name', 'patient__mrn']


@admin.register(ProcedureCatalog)
class ProcedureCatalogAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'standard_fee', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['code', 'name']


@admin.register(ClinicalVisit)
class ClinicalVisitAdmin(admin.ModelAdmin):
    list_display = ['patient', 'dentist', 'visit_date', 'blood_pressure', 'next_recall_date']


@admin.register(DentalLabOrder)
class DentalLabOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'lab_name', 'patient', 'work_type', 'shade', 'status', 'sent_date', 'expected_delivery']
    list_filter = ['status', 'work_type']


@admin.register(DentalMaterialInventory)
class DentalMaterialInventoryAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'category', 'current_stock', 'unit', 'reorder_threshold', 'unit_cost']
    list_filter = ['category']


admin.site.register(DentalOperatory)
admin.site.register(TreatmentItem)
admin.site.register(DentalRadiograph)
admin.site.register(Prescription)
admin.site.register(PrescriptionItem)
admin.site.register(Invoice)
admin.site.register(InvoiceItem)
admin.site.register(Payment)
