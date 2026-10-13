from django import forms
from .models import (
    User, Patient, Appointment, ClinicalVisit, TreatmentItem,
    DentalLabOrder, DentalRadiograph, Prescription, PrescriptionItem,
    Invoice, InvoiceItem, Payment, DentalMaterialInventory, ToothRecord,
    DentalConsentForm, WhatsAppNotification
)


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'mrn', 'first_name', 'last_name', 'phone', 'email',
            'date_of_birth', 'gender', 'blood_group', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'has_diabetes', 'has_hypertension', 'has_bleeding_disorder',
            'has_cardiac_condition', 'has_asthma', 'is_pregnant',
            'has_allergies', 'allergy_details', 'current_medications',
            'medical_history_notes'
        ]
        widgets = {
            'mrn': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. RKH-2026-0005'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+91 98765 43210'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'patient@example.com'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Residential address'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Phone Number'}),
            'allergy_details': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Penicillin, Sulfa, Latex'}),
            'current_medications': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'List active medications'}),
            'medical_history_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Additional clinical medical history'}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'dentist', 'chair', 'appointment_date', 'start_time', 'end_time', 'reason', 'status', 'notes']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'dentist': forms.Select(attrs={'class': 'form-select'}),
            'chair': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-input', 'type': 'time'}),
            'reason': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Reason for consultation / procedure'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Special notes or instructions'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['dentist'].queryset = User.objects.filter(role='DENTIST')
        self.fields['status'].required = False
        self.fields['status'].initial = 'SCHEDULED'
        self.fields['chair'].required = False
        self.fields['end_time'].required = False
        self.fields['notes'].required = False

    def clean_status(self):
        return self.cleaned_data.get('status') or 'SCHEDULED'


class ClinicalVisitForm(forms.ModelForm):
    class Meta:
        model = ClinicalVisit
        fields = [
            'patient', 'dentist', 'visit_date', 'chief_complaint',
            'history_of_illness', 'blood_pressure', 'pulse_rate', 'blood_sugar',
            'subjective', 'objective', 'assessment', 'treatment_plan',
            'next_recall_date'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'dentist': forms.Select(attrs={'class': 'form-select'}),
            'visit_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'chief_complaint': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Chief complaint in patient\'s words'}),
            'history_of_illness': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Onset, duration, severity, radiation of pain'}),
            'blood_pressure': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 120/80 mmHg'}),
            'pulse_rate': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 72'}),
            'blood_sugar': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. RBS 120 mg/dL'}),
            'subjective': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Symptoms, trigger factors (hot/cold/chewing)'}),
            'objective': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Intra-oral examination findings, percussion, mobility, soft tissue'}),
            'assessment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Final dental diagnosis'}),
            'treatment_plan': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Proposed treatment procedures'}),
            'next_recall_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class TreatmentItemForm(forms.ModelForm):
    class Meta:
        model = TreatmentItem
        fields = ['patient', 'dentist', 'procedure', 'tooth_number', 'status', 'cost', 'discount', 'notes', 'planned_date']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'dentist': forms.Select(attrs={'class': 'form-select'}),
            'procedure': forms.Select(attrs={'class': 'form-select'}),
            'tooth_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 16, 21-22, Full Mouth'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'cost': forms.NumberInput(attrs={'class': 'form-input'}),
            'discount': forms.NumberInput(attrs={'class': 'form-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'planned_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class DentalLabOrderForm(forms.ModelForm):
    class Meta:
        model = DentalLabOrder
        fields = [
            'order_number', 'lab_name', 'patient', 'dentist',
            'teeth_numbers', 'work_type', 'shade', 'sent_date',
            'expected_delivery', 'status', 'lab_charges', 'instructions'
        ]
        widgets = {
            'order_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. LAB-2026-0050'}),
            'lab_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Name of Dental Lab'}),
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'dentist': forms.Select(attrs={'class': 'form-select'}),
            'teeth_numbers': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 14, 15'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'shade': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. VITA A2, A3'}),
            'sent_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'expected_delivery': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'lab_charges': forms.NumberInput(attrs={'class': 'form-input'}),
            'instructions': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }


class DentalRadiographForm(forms.ModelForm):
    class Meta:
        model = DentalRadiograph
        fields = ['image_type', 'tooth_number', 'image_file', 'findings']
        widgets = {
            'image_type': forms.Select(attrs={'class': 'form-select'}),
            'tooth_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 36'}),
            'findings': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Radiographic interpretation'}),
        }


class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = DentalMaterialInventory
        fields = ['item_code', 'name', 'category', 'current_stock', 'unit', 'reorder_threshold', 'unit_cost', 'supplier_name', 'expiry_date']
        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'current_stock': forms.NumberInput(attrs={'class': 'form-input'}),
            'unit': forms.TextInput(attrs={'class': 'form-input'}),
            'reorder_threshold': forms.NumberInput(attrs={'class': 'form-input'}),
            'unit_cost': forms.NumberInput(attrs={'class': 'form-input'}),
            'supplier_name': forms.TextInput(attrs={'class': 'form-input'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        }


class DentalConsentFormForm(forms.ModelForm):
    class Meta:
        model = DentalConsentForm
        fields = [
            'procedure_type', 'title', 'tooth_number', 'consent_body',
            'signed_by_name', 'relationship_to_patient', 'witness_name',
            'patient_signature_data'
        ]
        widgets = {
            'procedure_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_procedure_type', 'onchange': 'loadConsentTemplate(this.value)'}),
            'title': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_title'}),
            'tooth_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. #36, #48, Full Mouth'}),
            'consent_body': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 9, 'id': 'id_consent_body'}),
            'signed_by_name': forms.TextInput(attrs={'class': 'form-input', 'id': 'id_signed_by_name'}),
            'relationship_to_patient': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Self, Parent, Spouse, Guardian'}),
            'witness_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Attending Dental Surgeon / Witness'}),
            'patient_signature_data': forms.HiddenInput(attrs={'id': 'id_patient_signature_data'}),
        }


class WhatsAppMessageForm(forms.Form):
    recipient_phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. +91 98765 43210'}))
    message_type = forms.ChoiceField(choices=WhatsAppNotification.MESSAGE_TYPES, widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_wa_type', 'onchange': 'loadWhatsAppTemplate(this.value)'}))
    message_content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-textarea', 'rows': 6, 'id': 'id_wa_content'}))

