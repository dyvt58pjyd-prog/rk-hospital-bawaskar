import json
import datetime
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db import models
import urllib.parse
from django.db.models import Q, Sum, Count, F
from django.utils import timezone

from .models import (
    User, Patient, DentalOperatory, Appointment, ToothRecord,
    ClinicalVisit, ProcedureCatalog, TreatmentItem, DentalLabOrder,
    DentalRadiograph, Prescription, PrescriptionItem, Invoice,
    InvoiceItem, Payment, DentalMaterialInventory,
    DentalConsentForm, WhatsAppNotification
)
from .forms import (
    PatientForm, AppointmentForm, ClinicalVisitForm, TreatmentItemForm,
    DentalLabOrderForm, DentalRadiographForm, InventoryItemForm,
    DentalConsentFormForm, WhatsAppMessageForm
)
from .consent_templates import CONSENT_TEMPLATES


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        u = request.POST.get('username', '').strip()
        p = request.POST.get('password', '')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome, {user.get_full_name() or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password. Please verify your credentials and try again.")

    return render(request, 'auth/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out safely.")
    return redirect('login')


@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()

    # If Patient Portal user, show patient-specific dashboard
    if user.is_patient_user():
        patient = getattr(user, 'patient_profile', None)
        if not patient:
            # Fallback for patient role without linked patient profile
            patient = Patient.objects.filter(phone=user.phone_number).first()
        
        my_appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date') if patient else []
        my_treatments = TreatmentItem.objects.filter(patient=patient).order_by('-planned_date') if patient else []
        my_prescriptions = Prescription.objects.filter(patient=patient).order_by('-prescription_date') if patient else []
        my_invoices = Invoice.objects.filter(patient=patient).order_by('-invoice_date') if patient else []
        my_teeth = ToothRecord.objects.filter(patient=patient) if patient else []

        context = {
            'patient': patient,
            'appointments': my_appointments,
            'treatments': my_treatments,
            'prescriptions': my_prescriptions,
            'invoices': my_invoices,
            'teeth': my_teeth,
        }
        return render(request, 'dashboard/patient_dashboard.html', context)

    # Common metrics for staff / doctors
    today_appointments = Appointment.objects.filter(appointment_date=today).select_related('patient', 'dentist', 'chair')
    checked_in_queue = today_appointments.filter(status__in=['CHECKED_IN', 'IN_CHAIR'])
    
    total_patients_count = Patient.objects.count()
    active_lab_orders_count = DentalLabOrder.objects.exclude(status='FITTED_OK').count()
    low_stock_count = DentalMaterialInventory.objects.filter(current_stock__lte=models.F('reorder_threshold') if hasattr(models, 'F') else 10).count()
    
    # Financial summary for admin
    monthly_invoices = Invoice.objects.filter(invoice_date__month=today.month, invoice_date__year=today.year)
    total_revenue_month = monthly_invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    pending_dues_month = monthly_invoices.aggregate(Sum('balance_amount'))['balance_amount__sum'] or Decimal('0.00')

    # Operatory chairs status
    operatories = DentalOperatory.objects.filter(is_active=True)
    chair_statuses = []
    for op in operatories:
        current_appt = today_appointments.filter(chair=op, status='IN_CHAIR').first()
        next_appt = today_appointments.filter(chair=op, status__in=['CONFIRMED', 'CHECKED_IN', 'SCHEDULED']).first()
        chair_statuses.append({
            'operatory': op,
            'current_appt': current_appt,
            'next_appt': next_appt,
            'is_occupied': bool(current_appt)
        })

    # Dentist specific queue
    my_queue = today_appointments.filter(dentist=user) if user.is_dentist() else today_appointments

    recent_patients = Patient.objects.all().order_by('-created_at')[:6]
    recent_visits = ClinicalVisit.objects.all().select_related('patient', 'dentist')[:5]
    low_stock_items = DentalMaterialInventory.objects.filter(current_stock__lte=15)[:5]
    active_lab_orders = DentalLabOrder.objects.exclude(status='FITTED_OK').select_related('patient', 'dentist')[:5]

    context = {
        'today': today,
        'today_appointments': today_appointments,
        'checked_in_queue': checked_in_queue,
        'my_queue': my_queue,
        'total_patients_count': total_patients_count,
        'active_lab_orders_count': active_lab_orders_count,
        'low_stock_count': low_stock_count,
        'total_revenue_month': total_revenue_month,
        'pending_dues_month': pending_dues_month,
        'chair_statuses': chair_statuses,
        'recent_patients': recent_patients,
        'recent_visits': recent_visits,
        'low_stock_items': low_stock_items,
        'active_lab_orders': active_lab_orders,
    }

    if user.is_admin():
        return render(request, 'dashboard/admin_dashboard.html', context)
    elif user.is_dentist():
        return render(request, 'dashboard/dentist_dashboard.html', context)
    elif user.is_receptionist():
        return render(request, 'dashboard/receptionist_dashboard.html', context)
    elif user.is_pharmacist():
        return render(request, 'dashboard/pharmacist_dashboard.html', context)
    elif user.is_hygienist():
        return render(request, 'dashboard/hygienist_dashboard.html', context)
    else:
        return render(request, 'dashboard/admin_dashboard.html', context)


# ==========================================
# PATIENT 360 & CLINICAL EMR
# ==========================================

@login_required
def patient_list(request):
    query = request.GET.get('q', '').strip()
    alert_filter = request.GET.get('alert', '')

    patients = Patient.objects.all()

    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(mrn__icontains=query) |
            Q(phone__icontains=query)
        )

    if alert_filter == 'diabetes':
        patients = patients.filter(has_diabetes=True)
    elif alert_filter == 'hypertension':
        patients = patients.filter(has_hypertension=True)
    elif alert_filter == 'allergy':
        patients = patients.filter(has_allergies=True)
    elif alert_filter == 'cardiac':
        patients = patients.filter(has_cardiac_condition=True)
    elif alert_filter == 'bleeding':
        patients = patients.filter(has_bleeding_disorder=True)

    return render(request, 'patients/patient_list.html', {
        'patients': patients,
        'query': query,
        'alert_filter': alert_filter,
    })


@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient {patient.full_name} ({patient.mrn}) registered successfully!")
            return redirect('patient_detail', pk=patient.pk)
    else:
        # Generate next suggested MRN
        count = Patient.objects.count() + 1
        year = timezone.now().year
        suggested_mrn = f"RKH-{year}-{count:04d}"
        form = PatientForm(initial={'mrn': suggested_mrn})

    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Register New Patient'})


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient {patient.full_name} updated successfully!")
            return redirect('patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)

    return render(request, 'patients/patient_form.html', {'form': form, 'title': f'Edit Patient - {patient.full_name}', 'patient': patient})


def build_quadrant_teeth(teeth_dict, numbers):
    quad = []
    for num in numbers:
        rec = teeth_dict.get(num)
        quad.append({
            'num': num,
            'status': rec.status if rec else 'HEALTHY',
            'status_display': rec.get_status_display() if rec else 'Healthy / Sound',
            'buccal': rec.buccal if rec else False,
            'lingual': rec.lingual if rec else False,
            'mesial': rec.mesial if rec else False,
            'distal': rec.distal if rec else False,
            'occlusal': rec.occlusal if rec else False,
            'pocket_depth_mm': rec.pocket_depth_mm if rec else 2,
            'mobility': rec.mobility if rec else 0,
            'bleeding_on_probing': rec.bleeding_on_probing if rec else False,
            'notes': rec.clinical_notes if rec else '',
        })
    return quad


@login_required
def patient_detail(request, pk):
    # Enforce role-based access for patient accounts
    if request.user.is_patient_user():
        patient_prof = getattr(request.user, 'patient_profile', None)
        if patient_prof and patient_prof.id != pk:
            messages.warning(request, "You can only view your own medical records.")
            return redirect('patient_detail', pk=patient_prof.id)

    patient = get_object_or_404(Patient, pk=pk)
    active_tab = request.GET.get('tab', 'chart')

    # Odontogram records
    teeth = ToothRecord.objects.filter(patient=patient)
    teeth_dict = {t.tooth_number: t for t in teeth}

    # Pre-build structured tooth quadrant lists for adult and pediatric
    quadrant_1 = build_quadrant_teeth(teeth_dict, [18, 17, 16, 15, 14, 13, 12, 11])
    quadrant_2 = build_quadrant_teeth(teeth_dict, [21, 22, 23, 24, 25, 26, 27, 28])
    quadrant_4 = build_quadrant_teeth(teeth_dict, [48, 47, 46, 45, 44, 43, 42, 41])
    quadrant_3 = build_quadrant_teeth(teeth_dict, [31, 32, 33, 34, 35, 36, 37, 38])

    pedia_q5 = build_quadrant_teeth(teeth_dict, [55, 54, 53, 52, 51])
    pedia_q6 = build_quadrant_teeth(teeth_dict, [61, 62, 63, 64, 65])
    pedia_q8 = build_quadrant_teeth(teeth_dict, [85, 84, 83, 82, 81])
    pedia_q7 = build_quadrant_teeth(teeth_dict, [71, 72, 73, 74, 75])

    # Clinical Visits
    visits = patient.clinical_visits.all().select_related('dentist')
    # Treatments
    treatments = patient.treatment_items.all().select_related('procedure', 'dentist')
    # Prescriptions
    prescriptions = patient.prescriptions.all().prefetch_related('items').select_related('dentist')
    # Lab orders
    lab_orders = patient.lab_orders.all().select_related('dentist')
    # Radiographs
    radiographs = patient.radiographs.all().select_related('dentist')
    # Invoices & billing
    invoices = patient.invoices.all().prefetch_related('items', 'payments')
    # Appointments
    appointments = patient.appointments.all().select_related('dentist', 'chair')
    # Digital Consent Forms
    consent_forms = patient.consent_forms.all().select_related('dentist')
    # WhatsApp message logs
    whatsapp_messages = patient.whatsapp_messages.all().select_related('sent_by')

    # Available dentists for modals
    dentists = User.objects.filter(role__in=['DENTIST', 'ADMIN'])
    procedures = ProcedureCatalog.objects.filter(is_active=True)

    # Totals
    total_billed = invoices.aggregate(Sum('net_payable'))['net_payable__sum'] or Decimal('0.00')
    total_paid = invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    total_balance = invoices.aggregate(Sum('balance_amount'))['balance_amount__sum'] or Decimal('0.00')

    context = {
        'patient': patient,
        'active_tab': active_tab,
        'teeth_dict': teeth_dict,
        'quadrant_1': quadrant_1,
        'quadrant_2': quadrant_2,
        'quadrant_4': quadrant_4,
        'quadrant_3': quadrant_3,
        'pedia_q5': pedia_q5,
        'pedia_q6': pedia_q6,
        'pedia_q8': pedia_q8,
        'pedia_q7': pedia_q7,
        'visits': visits,
        'treatments': treatments,
        'prescriptions': prescriptions,
        'lab_orders': lab_orders,
        'radiographs': radiographs,
        'invoices': invoices,
        'appointments': appointments,
        'consent_forms': consent_forms,
        'whatsapp_messages': whatsapp_messages,
        'dentists': dentists,
        'operatories': DentalOperatory.objects.filter(is_active=True),
        'procedures': procedures,
        'total_billed': total_billed,
        'total_paid': total_paid,
        'total_balance': total_balance,
        'medical_alerts': patient.get_active_medical_alerts(),
    }
    return render(request, 'patients/patient_detail.html', context)



# ==========================================
# DENTAL EMR & ODONTOGRAM API
# ==========================================

def build_initial_odontogram_state(patient):
    """Construct baseline react-advanced-odontogram state from existing ToothRecord entries."""
    adult_teeth = [
        18, 17, 16, 15, 14, 13, 12, 11,
        21, 22, 23, 24, 25, 26, 27, 28,
        48, 47, 46, 45, 44, 43, 42, 41,
        31, 32, 33, 34, 35, 36, 37, 38,
    ]
    records = {r.tooth_number: r for r in patient.tooth_records.all()}
    teeth_dict = {}

    for t_num in adult_teeth:
        t_key = str(t_num)
        rec = records.get(t_num)
        if not rec or rec.status == 'HEALTHY':
            teeth_dict[t_key] = {
                'toothSelection': 'healthy',
                'caries': [],
                'fillings': {'surfaces': []},
            }
            continue

        surfs = []
        if rec.mesial: surfs.append('mesial')
        if rec.distal: surfs.append('distal')
        if rec.occlusal: surfs.append('occlusal')
        if rec.buccal: surfs.append('buccal')
        if rec.lingual: surfs.append('lingual')

        t_data = {
            'toothSelection': 'healthy',
            'caries': [],
            'fillings': {'surfaces': []},
        }

        if rec.status == 'CARIES':
            t_data['caries'] = surfs if surfs else ['occlusal']
        elif rec.status == 'FILLED':
            t_data['fillings'] = {'surfaces': surfs if surfs else ['occlusal'], 'material': 'composite'}
            t_data['fillingSurfaces'] = surfs if surfs else ['occlusal']
            t_data['fillingMaterial'] = 'composite'
        elif rec.status == 'RCT':
            t_data['endo'] = 'rct'
            t_data['toothSubstrate'] = 'natural'
        elif rec.status == 'CROWN':
            t_data['restorationType'] = 'crown'
            t_data['restorationMaterial'] = 'metal-ceramic'
            t_data['toothSubstrate'] = 'crownprep'
        elif rec.status == 'IMPLANT':
            t_data['toothSelection'] = 'implant'
            t_data['restorationType'] = 'crown'
            t_data['restorationMaterial'] = 'zircon'
        elif rec.status == 'MISSING':
            t_data['toothSelection'] = 'missing'
        elif rec.status == 'IMPACTED':
            t_data['toothSelection'] = 'impacted'
        elif rec.status == 'FRACTURED':
            t_data['toothSubstrate'] = 'broken'

        teeth_dict[t_key] = t_data

    return {
        'version': '2.22',
        'globals': {
            'wisdomVisible': True,
            'showBase': True,
            'occlusalVisible': True,
            'showHealthyPulp': False,
            'edentulous': False,
        },
        'teeth': teeth_dict,
    }


@login_required
def odontogram_studio(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    read_only = request.user.role in ['PATIENT', 'RECEPTION', 'PHARMACY']
    return render(request, 'emr/odontogram_studio.html', {
        'patient': patient,
        'read_only': read_only,
    })


@login_required
def api_odontogram_state(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'GET':
        chart_data = patient.odontogram_state or {}
        if not chart_data or not isinstance(chart_data, dict) or not chart_data.get('teeth'):
            chart_data = build_initial_odontogram_state(patient)

        return JsonResponse({
            'success': True,
            'patient_id': patient.id,
            'patient_name': patient.full_name,
            'patient_mrn': patient.mrn,
            'chart_data': chart_data,
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            chart_data = data.get('chart_data', {})
            patient.odontogram_state = chart_data
            patient.save(update_fields=['odontogram_state'])

            # Sync individual ToothRecord relational rows
            teeth = chart_data.get('teeth', {})
            if isinstance(teeth, dict):
                for t_str, t_info in teeth.items():
                    try:
                        t_num = int(t_str)
                    except (ValueError, TypeError):
                        continue

                    if not isinstance(t_info, dict):
                        continue

                    record, _ = ToothRecord.objects.get_or_create(
                        patient=patient,
                        tooth_number=t_num,
                        defaults={'status': 'HEALTHY'}
                    )

                    caries = t_info.get('caries', [])
                    fillings = t_info.get('fillings', {})
                    filling_surfs = t_info.get('fillingSurfaces', [])
                    root_perio = t_info.get('rootPerio', {})
                    prosthetics = t_info.get('prosthetics', {}) or {}
                    tooth_selection = str(t_info.get('toothSelection', 'healthy')).lower()
                    restoration_type = str(t_info.get('restorationType', 'none')).lower()
                    substrate = str(t_info.get('toothSubstrate', 'natural')).lower()
                    endo = str(t_info.get('endo', 'none')).lower()

                    mesial = False
                    distal = False
                    occlusal = False
                    buccal = False
                    lingual = False

                    # Caries surfaces check
                    if isinstance(caries, list):
                        for s in caries:
                            s_str = str(s).lower()
                            if 'm' in s_str: mesial = True
                            if 'd' in s_str: distal = True
                            if 'o' in s_str or 'i' in s_str: occlusal = True
                            if 'b' in s_str or 'v' in s_str: buccal = True
                            if 'l' in s_str or 'p' in s_str: lingual = True

                    # Filling surfaces check
                    if isinstance(fillings, dict) and fillings.get('surfaces'):
                        for s in fillings.get('surfaces', []):
                            s_str = str(s.get('surface', s) if isinstance(s, dict) else s).lower()
                            if 'm' in s_str: mesial = True
                            if 'd' in s_str: distal = True
                            if 'o' in s_str or 'i' in s_str: occlusal = True
                            if 'b' in s_str or 'v' in s_str: buccal = True
                            if 'l' in s_str or 'p' in s_str: lingual = True
                    elif isinstance(filling_surfs, list):
                        for s in filling_surfs:
                            s_str = str(s).lower()
                            if 'm' in s_str: mesial = True
                            if 'd' in s_str: distal = True
                            if 'o' in s_str or 'i' in s_str: occlusal = True
                            if 'b' in s_str or 'v' in s_str: buccal = True
                            if 'l' in s_str or 'p' in s_str: lingual = True

                    # Determine status
                    status = 'HEALTHY'
                    if tooth_selection in ['missing', 'extracted']:
                        status = 'MISSING'
                    elif tooth_selection in ['implant']:
                        status = 'IMPLANT'
                    elif tooth_selection in ['impacted']:
                        status = 'IMPACTED'
                    elif restoration_type in ['crown', 'bridge']:
                        status = 'CROWN'
                    elif endo in ['rct', 'treated']:
                        status = 'RCT'
                    elif substrate in ['broken', 'radix']:
                        status = 'FRACTURED'
                    elif (isinstance(fillings, dict) and fillings.get('surfaces')) or filling_surfs:
                        status = 'FILLED'
                    elif caries and len(caries) > 0:
                        status = 'CARIES'

                    record.status = status
                    record.mesial = mesial
                    record.distal = distal
                    record.occlusal = occlusal
                    record.buccal = buccal
                    record.lingual = lingual
                    record.last_updated_by = request.user
                    record.save()

            return JsonResponse({
                'success': True,
                'message': 'Visual dental chart synchronized with patient EMR records',
                'saved_at': timezone.now().strftime('%H:%M:%S'),
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)




@login_required
def api_tooth_record(request, patient_id, tooth_number):
    patient = get_object_or_404(Patient, pk=patient_id)
    tooth_number = int(tooth_number)

    record, created = ToothRecord.objects.get_or_create(
        patient=patient,
        tooth_number=tooth_number,
        defaults={'status': 'HEALTHY'}
    )

    if request.method == 'GET':
        return JsonResponse({
            'tooth_number': record.tooth_number,
            'status': record.status,
            'status_display': record.get_status_display(),
            'mesial': record.mesial,
            'distal': record.distal,
            'occlusal': record.occlusal,
            'buccal': record.buccal,
            'lingual': record.lingual,
            'pocket_depth_mm': record.pocket_depth_mm,
            'mobility': record.mobility,
            'bleeding_on_probing': record.bleeding_on_probing,
            'plaque_present': record.plaque_present,
            'calculus_present': record.calculus_present,
            'clinical_notes': record.clinical_notes or '',
            'updated_at': record.updated_at.strftime('%Y-%m-%d %H:%M') if record.updated_at else '',
        })

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            record.status = data.get('status', record.status)
            record.mesial = bool(data.get('mesial', record.mesial))
            record.distal = bool(data.get('distal', record.distal))
            record.occlusal = bool(data.get('occlusal', record.occlusal))
            record.buccal = bool(data.get('buccal', record.buccal))
            record.lingual = bool(data.get('lingual', record.lingual))
            record.pocket_depth_mm = int(data.get('pocket_depth_mm', record.pocket_depth_mm or 2))
            record.mobility = int(data.get('mobility', record.mobility or 0))
            record.bleeding_on_probing = bool(data.get('bleeding_on_probing', False))
            record.clinical_notes = data.get('clinical_notes', record.clinical_notes)
            record.last_updated_by = request.user
            record.save()

            # Optionally create a Treatment Item directly from tooth modal
            proc_id = data.get('procedure_id')
            if proc_id:
                procedure = ProcedureCatalog.objects.filter(id=proc_id).first()
                if procedure:
                    TreatmentItem.objects.create(
                        patient=patient,
                        dentist=request.user if request.user.is_dentist() else User.objects.filter(role='DENTIST').first() or request.user,
                        procedure=procedure,
                        tooth_number=str(tooth_number),
                        status='PLANNED',
                        cost=procedure.standard_fee,
                        notes=f"Planned from Dental Chart: {data.get('clinical_notes', '')}"
                    )

            return JsonResponse({'success': True, 'message': f'Tooth #{tooth_number} updated successfully', 'status': record.status, 'status_display': record.get_status_display()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


# ==========================================
# CLINICAL VISITS & SOAP NOTES
# ==========================================

@login_required
def clinical_visit_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = ClinicalVisitForm(request.POST)
        if form.is_valid():
            visit = form.save(commit=False)
            visit.patient = patient
            if not visit.dentist_id:
                visit.dentist = request.user if request.user.is_dentist() else User.objects.filter(role='DENTIST').first() or request.user
            visit.save()
            messages.success(request, f"Clinical Visit recorded for {patient.full_name}!")
            return redirect(f"/patients/{patient.id}/?tab=visits")
    else:
        form = ClinicalVisitForm(initial={'patient': patient, 'dentist': request.user if request.user.is_dentist() else None, 'visit_date': timezone.now().date()})

    return render(request, 'emr/clinical_visit_form.html', {'form': form, 'patient': patient})


@login_required
def clinical_visit_detail(request, pk):
    visit = get_object_or_404(ClinicalVisit, pk=pk)
    return render(request, 'emr/clinical_visit_detail.html', {'visit': visit, 'patient': visit.patient})


# ==========================================
# TREATMENT PLANNING & PROCEDURES
# ==========================================

@login_required
def treatment_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = TreatmentItemForm(request.POST)
        if form.is_valid():
            treatment = form.save(commit=False)
            treatment.patient = patient
            treatment.save()
            messages.success(request, f"Procedure '{treatment.procedure.name}' added to treatment plan!")
            return redirect(f"/patients/{patient.id}/?tab=treatments")
    else:
        form = TreatmentItemForm(initial={'patient': patient, 'dentist': request.user if request.user.is_dentist() else None})

    return render(request, 'emr/treatment_form.html', {'form': form, 'patient': patient})


@login_required
def treatment_update_status(request, pk):
    treatment = get_object_or_404(TreatmentItem, pk=pk)
    new_status = request.POST.get('status')
    if new_status in ['PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']:
        treatment.status = new_status
        if new_status == 'COMPLETED':
            treatment.completed_date = timezone.now()
        treatment.save()
        messages.success(request, f"Treatment #{treatment.id} updated to {treatment.get_status_display()}.")
    return redirect(f"/patients/{treatment.patient.id}/?tab=treatments")


# ==========================================
# APPOINTMENTS & OPERATORY QUEUE
# ==========================================

@login_required
def appointment_list(request):
    selected_date_str = request.GET.get('date')
    if selected_date_str:
        try:
            selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().date()
    else:
        selected_date = timezone.now().date()

    appointments = Appointment.objects.filter(appointment_date=selected_date).select_related('patient', 'dentist', 'chair').order_by('start_time')
    operatories = DentalOperatory.objects.filter(is_active=True)
    dentists = User.objects.filter(role__in=['DENTIST', 'ADMIN'])

    # Organize appointments by chair
    chair_schedule = []
    for op in operatories:
        chair_appts = appointments.filter(chair=op)
        chair_schedule.append({
            'operatory': op,
            'appointments': chair_appts,
        })

    form = AppointmentForm(initial={'appointment_date': selected_date})

    context = {
        'selected_date': selected_date,
        'appointments': appointments,
        'chair_schedule': chair_schedule,
        'operatories': operatories,
        'dentists': dentists,
        'form': form,
    }
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def appointment_create(request):
    redirect_target = request.POST.get('redirect_to', 'appointment_list')
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            if not appt.status:
                appt.status = 'SCHEDULED'
            appt.save()
            messages.success(request, f"Appointment booked for {appt.patient.full_name} with Dr. {appt.dentist.get_full_name() or appt.dentist.username} on {appt.appointment_date} at {appt.start_time}!")
            if redirect_target == 'dashboard':
                return redirect('dashboard')
            elif redirect_target == 'patient':
                return redirect(f"/patients/{appt.patient.id}/?tab=appointments")
            return redirect('appointment_list')
        else:
            for field, errs in form.errors.items():
                label = form.fields[field].label if field in form.fields and form.fields[field].label else field
                messages.error(request, f"Appointment booking error ({label}): {', '.join(errs)}")
    return redirect('appointment_list')


@login_required
def appointment_update_status(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Appointment.STATUS_CHOICES):
        appt.status = new_status
        appt.save()
        messages.success(request, f"Appointment status updated to {appt.get_status_display()} for {appt.patient.full_name}.")
    
    redirect_to = request.POST.get('redirect_to', 'appointment_list')
    if redirect_to == 'dashboard':
        return redirect('dashboard')
    elif redirect_to == 'patient':
        return redirect(f"/patients/{appt.patient.id}/?tab=appointments")
    return redirect('appointment_list')


# ==========================================
# DENTAL LAB ORDERS
# ==========================================

@login_required
def lab_list(request):
    status_filter = request.GET.get('status', '')
    orders = DentalLabOrder.objects.all().select_related('patient', 'dentist')
    if status_filter:
        orders = orders.filter(status=status_filter)

    form = DentalLabOrderForm()
    return render(request, 'lab/lab_list.html', {
        'orders': orders,
        'status_filter': status_filter,
        'form': form,
        'status_choices': DentalLabOrder.STATUS_CHOICES,
    })


@login_required
def lab_create(request):
    if request.method == 'POST':
        form = DentalLabOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, f"Lab order {order.order_number} ({order.get_work_type_display()}) created!")
            return redirect('lab_list')
    return redirect('lab_list')


@login_required
def lab_update_status(request, pk):
    order = get_object_or_404(DentalLabOrder, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(DentalLabOrder.STATUS_CHOICES):
        order.status = new_status
        if new_status == 'RECEIVED' and not order.received_date:
            order.received_date = timezone.now().date()
        order.save()
        messages.success(request, f"Lab Order #{order.order_number} updated to {order.get_status_display()}!")
    return redirect('lab_list')


# ==========================================
# DIGITAL DENTAL PRESCRIPTIONS (Rx)
# ==========================================

@login_required
def prescription_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        dentist_id = request.POST.get('dentist')
        dentist = User.objects.filter(id=dentist_id).first() or request.user
        general_advice = request.POST.get('general_advice', '')

        prescription = Prescription.objects.create(
            patient=patient,
            dentist=dentist,
            general_advice=general_advice
        )

        med_names = request.POST.getlist('medicine_name[]')
        med_forms = request.POST.getlist('form[]')
        med_dosages = request.POST.getlist('dosage[]')
        med_freqs = request.POST.getlist('frequency[]')
        med_durations = request.POST.getlist('duration[]')
        med_insts = request.POST.getlist('instructions[]')

        for i in range(len(med_names)):
            name = med_names[i].strip()
            if name:
                PrescriptionItem.objects.create(
                    prescription=prescription,
                    medicine_name=name,
                    form=med_forms[i] if i < len(med_forms) else 'TABLET',
                    dosage=med_dosages[i] if i < len(med_dosages) else '1 Tab',
                    frequency=med_freqs[i] if i < len(med_freqs) else 'TDS',
                    duration=med_durations[i] if i < len(med_durations) else '5 days',
                    instructions=med_insts[i] if i < len(med_insts) else 'After food',
                )

        messages.success(request, f"Prescription #{prescription.id} issued successfully!")
        return redirect('prescription_print', pk=prescription.id)

    dentists = User.objects.filter(role__in=['DENTIST', 'ADMIN'])
    return render(request, 'prescriptions/prescription_form.html', {
        'patient': patient,
        'dentists': dentists,
    })


@login_required
def prescription_print(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    return render(request, 'prescriptions/prescription_print.html', {'rx': prescription, 'patient': prescription.patient})


# ==========================================
# BILLING, INVOICING & PAYMENTS
# ==========================================

@login_required
def billing_list(request):
    invoices = Invoice.objects.all().select_related('patient', 'created_by').prefetch_related('payments')
    total_revenue = invoices.aggregate(Sum('paid_amount'))['paid_amount__sum'] or Decimal('0.00')
    total_due = invoices.aggregate(Sum('balance_amount'))['balance_amount__sum'] or Decimal('0.00')

    return render(request, 'billing/billing_list.html', {
        'invoices': invoices,
        'total_revenue': total_revenue,
        'total_due': total_due,
    })


@login_required
def invoice_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        # Generate Invoice Number
        count = Invoice.objects.count() + 1
        year = timezone.now().year
        inv_number = f"INV-{year}-{count:04d}"

        discount = Decimal(request.POST.get('discount_amount', '0.00') or '0.00')
        notes = request.POST.get('notes', '')

        invoice = Invoice.objects.create(
            invoice_number=inv_number,
            patient=patient,
            created_by=request.user,
            discount_amount=discount,
            notes=notes
        )

        item_descs = request.POST.getlist('item_desc[]')
        item_qtys = request.POST.getlist('item_qty[]')
        item_prices = request.POST.getlist('item_price[]')

        for i in range(len(item_descs)):
            desc = item_descs[i].strip()
            if desc:
                qty = int(item_qtys[i] or 1)
                unit_price = Decimal(item_prices[i] or '0.00')
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=desc,
                    quantity=qty,
                    unit_price=unit_price,
                    total_price=unit_price * qty
                )

        # Initial payment if provided
        initial_pay = Decimal(request.POST.get('initial_payment', '0.00') or '0.00')
        pay_method = request.POST.get('payment_method', 'UPI')
        pay_ref = request.POST.get('transaction_ref', '')
        if initial_pay > Decimal('0.00'):
            Payment.objects.create(
                invoice=invoice,
                amount=initial_pay,
                payment_method=pay_method,
                transaction_reference=pay_ref,
                received_by=request.user
            )

        invoice.update_totals()
        messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
        return redirect('invoice_detail', pk=invoice.id)

    # Pre-load unbilled treatment items for easy auto-import!
    unbilled_treatments = patient.treatment_items.all()
    procedures = ProcedureCatalog.objects.filter(is_active=True)

    return render(request, 'billing/invoice_form.html', {
        'patient': patient,
        'unbilled_treatments': unbilled_treatments,
        'procedures': procedures,
    })


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'billing/invoice_detail.html', {'invoice': invoice, 'patient': invoice.patient})


@login_required
def invoice_add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', '0.00') or '0.00')
        method = request.POST.get('payment_method', 'UPI')
        ref = request.POST.get('transaction_reference', '')
        notes = request.POST.get('notes', '')

        if amount > 0:
            Payment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_method=method,
                transaction_reference=ref,
                received_by=request.user,
                notes=notes
            )
            invoice.update_totals()
            messages.success(request, f"Payment of ₹{amount} recorded for Invoice {invoice.invoice_number}!")
    return redirect('invoice_detail', pk=invoice.id)


# ==========================================
# DENTAL MATERIAL INVENTORY
# ==========================================

@login_required
def inventory_list(request):
    cat = request.GET.get('category', '')
    items = DentalMaterialInventory.objects.all()
    if cat:
        items = items.filter(category=cat)

    form = InventoryItemForm()
    return render(request, 'inventory/inventory_list.html', {
        'items': items,
        'selected_category': cat,
        'form': form,
        'categories': DentalMaterialInventory.CATEGORY_CHOICES,
    })


@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f"Dental material '{item.name}' added to inventory!")
            return redirect('inventory_list')
    return redirect('inventory_list')


@login_required
def inventory_stock_adjust(request, pk):
    item = get_object_or_404(DentalMaterialInventory, pk=pk)
    if request.method == 'POST':
        try:
            adj = int(request.POST.get('adjustment', 0))
            item.current_stock = max(0, item.current_stock + adj)
            item.save()
            messages.success(request, f"Updated stock for {item.name}: Now {item.current_stock} {item.unit}")
        except ValueError:
            messages.error(request, "Invalid adjustment value.")
    return redirect('inventory_list')


# ==========================================
# RADIOGRAPH (X-RAY) UPLOAD
# ==========================================

@login_required
def radiograph_upload(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = DentalRadiographForm(request.POST, request.FILES)
        if form.is_valid():
            rad = form.save(commit=False)
            rad.patient = patient
            if request.user.is_dentist():
                rad.dentist = request.user
            else:
                rad.dentist = User.objects.filter(role='DENTIST').first() or request.user
            rad.save()
            messages.success(request, f"Dental radiograph '{rad.get_image_type_display()}' uploaded and attached successfully!")
            return redirect(f"/patients/{patient.id}/?tab=radiographs")
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"Upload error ({field}): {err}")
    return redirect(f"/patients/{patient.id}/?tab=radiographs")


# ==========================================
# PAPERLESS DIGITAL CONSENT FORMS
# ==========================================

@login_required
def consent_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = DentalConsentFormForm(request.POST)
        if form.is_valid():
            consent = form.save(commit=False)
            consent.patient = patient
            if request.user.is_dentist() or request.user.is_admin():
                consent.dentist = request.user
            else:
                consent.dentist = User.objects.filter(role__in=['DENTIST', 'ADMIN']).first()

            sig_data = request.POST.get('patient_signature_data')
            if sig_data and len(sig_data) > 100:
                consent.patient_signature_data = sig_data
                consent.is_signed = True
                consent.signed_at = timezone.now()

            consent.save()
            messages.success(request, f"Informed Consent for '{consent.title}' recorded and signed successfully!")
            return redirect('consent_detail', consent_id=consent.id)
        else:
            for f, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f"{f}: {err}")
    else:
        proc_type = request.GET.get('type', 'IMPLANT')
        tpl = CONSENT_TEMPLATES.get(proc_type, CONSENT_TEMPLATES['GENERAL'])
        form = DentalConsentFormForm(initial={
            'procedure_type': proc_type,
            'title': tpl['title'],
            'consent_body': tpl['body'],
            'signed_by_name': patient.full_name,
            'relationship_to_patient': 'Self',
            'witness_name': request.user.get_full_name() or request.user.username,
        })

    return render(request, 'consents/consent_form.html', {
        'patient': patient,
        'form': form,
        'templates_json': json.dumps(CONSENT_TEMPLATES),
    })


@login_required
def consent_detail(request, consent_id):
    consent = get_object_or_404(
        DentalConsentForm.objects.select_related('patient', 'dentist'),
        pk=consent_id
    )
    return render(request, 'consents/consent_detail.html', {'consent': consent})


@login_required
def api_consent_template(request):
    proc_type = request.GET.get('procedure_type', 'GENERAL')
    tpl = CONSENT_TEMPLATES.get(proc_type, CONSENT_TEMPLATES['GENERAL'])
    return JsonResponse(tpl)


# ==========================================
# WHATSAPP AUTOMATED CLINICAL NOTIFICATIONS
# ==========================================

@login_required
def whatsapp_send(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    clean_phone = ''.join(ch for ch in (patient.phone or '') if ch.isdigit())
    if len(clean_phone) == 10:
        clean_phone = '91' + clean_phone  # Standard Indian country code

    msg_type = request.POST.get('message_type') or request.GET.get('type', 'APPT_CONFIRM')
    custom_text = request.POST.get('message_content')

    default_texts = {
        'APPT_CONFIRM': (
            f"🏥 *RK Hospital Bawaskar - Dental EMR Alert*\n\n"
            f"Dear {patient.full_name},\n"
            f"Your dental appointment has been scheduled and confirmed.\n\n"
            f"📍 *Location:* RK Hospital Bawaskar, Centre of Dental Excellence, Nagpur Road.\n"
            f"📞 *Hospital Helpdesk:* +91 98220 11223\n\n"
            f"Please arrive 10 minutes before your scheduled slot. Thank you!"
        ),
        'APPT_REMINDER': (
            f"⏰ *Friendly Appointment Reminder • RK Hospital Bawaskar*\n\n"
            f"Dear {patient.full_name},\n"
            f"This is a reminder for your upcoming dental visit with Dr. Bawaskar's clinical team.\n\n"
            f"If you need to reschedule, kindly notify the desk at +91 98220 11223."
        ),
        'POST_OP_EXTRACTION': (
            f"🦷 *Post-Extraction Care Instructions • RK Hospital Bawaskar*\n\n"
            f"Dear {patient.full_name},\n"
            f"Please strictly observe the following post-surgical instructions:\n"
            f"1. Keep sterile cotton gauze pressed firmly over the socket for 45 minutes.\n"
            f"2. ❌ DO NOT spit, rinse forcefully, or drink with a straw for 24 hours.\n"
            f"3. Apply cold ice pack on the cheek in intervals (15 mins on / 15 mins off).\n"
            f"4. Consume cold/soft foods. Strictly avoid hot or spicy foods.\n"
            f"5. Take prescribed pain relievers and antibiotics strictly after meals.\n\n"
            f"🚨 *Emergency Hotline:* +91 98220 11223 (Dr. Bawaskar)"
        ),
        'POST_OP_RCT': (
            f"🦷 *Post-Root Canal Treatment Care • RK Hospital Bawaskar*\n\n"
            f"Dear {patient.full_name},\n"
            f"1. Numbness will wear off in 2-3 hours; be careful not to bite your cheek or tongue.\n"
            f"2. Do NOT chew hard or sticky foods on the treated side until the final crown is fitted.\n"
            f"3. Mild tenderness for 2-3 days is normal and manageable with prescribed medicine.\n"
            f"4. Complete your prescribed medication course.\n\n"
            f"Next step: Permanent crown measurement and shade selection."
        ),
        'POST_OP_IMPLANT': (
            f"🦷 *Post-Dental Implant Care • RK Hospital Bawaskar*\n\n"
            f"Dear {patient.full_name},\n"
            f"1. Avoid touching or prodding the surgical site or sutures with your tongue/finger.\n"
            f"2. Maintain gentle oral hygiene; do not brush aggressively over the implant for 48 hours.\n"
            f"3. Strictly avoid smoking for at least 7 days to ensure osseointegration.\n"
            f"4. Suture removal scheduled in 7-10 days."
        ),
        'INVOICE_RECEIPT': (
            f"🧾 *Digital Receipt • RK Hospital Bawaskar*\n\n"
            f"Dear {patient.full_name},\n"
            f"Thank you for your visit. Your treatment and payment invoice have been registered in your dental EMR.\n\n"
            f"RK Hospital Bawaskar • Centre of Dental Excellence"
        )
    }

    final_text = custom_text or default_texts.get(msg_type, default_texts['APPT_CONFIRM'])
    wa_url = f"https://wa.me/{clean_phone}?text={urllib.parse.quote(final_text)}"

    # Record notification log
    WhatsAppNotification.objects.create(
        patient=patient,
        sent_by=request.user,
        recipient_phone=clean_phone or patient.phone or 'N/A',
        message_type=msg_type,
        message_content=final_text,
        click_to_chat_url=wa_url
    )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('ajax') == '1':
        return JsonResponse({'status': 'ok', 'whatsapp_url': wa_url})

    return redirect(wa_url)

