from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from decimal import Decimal


class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Hospital Director / Admin'),
        ('DENTIST', 'Dental Surgeon / Specialist'),
        ('RECEPTIONIST', 'Front Desk / OPD Coordinator'),
        ('HYGIENIST', 'Dental Hygienist / Nurse'),
        ('PHARMACIST', 'Pharmacist / Inventory Store'),
        ('PATIENT', 'Patient Portal'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='DENTIST')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True,
                                      help_text="e.g. Endodontist, Orthodontist, Periodontist, Oral Surgeon")
    qualification = models.CharField(max_length=100, blank=True, null=True,
                                     help_text="e.g. BDS, MDS (Oral & Maxillofacial Surgery)")
    license_number = models.CharField(max_length=50, blank=True, null=True,
                                      help_text="State Dental Council Reg. No.")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser

    def is_dentist(self):
        return self.role == 'DENTIST'

    def is_receptionist(self):
        return self.role == 'RECEPTIONIST'

    def is_hygienist(self):
        return self.role == 'HYGIENIST'

    def is_pharmacist(self):
        return self.role == 'PHARMACIST'

    def is_patient_user(self):
        return self.role == 'PATIENT'

    def get_role_badge_class(self):
        classes = {
            'ADMIN': 'bg-rose-500 text-white',
            'DENTIST': 'bg-cyan-600 text-white',
            'RECEPTIONIST': 'bg-amber-500 text-white',
            'HYGIENIST': 'bg-emerald-600 text-white',
            'PHARMACIST': 'bg-purple-600 text-white',
            'PATIENT': 'bg-blue-500 text-white',
        }
        return classes.get(self.role, 'bg-gray-500 text-white')

    def __str__(self):
        role_label = dict(self.ROLE_CHOICES).get(self.role, self.role)
        full_name = self.get_full_name() or self.username
        return f"{full_name} ({role_label})"


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_profile')
    mrn = models.CharField(max_length=30, unique=True, verbose_name="Medical Record Number")
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    address = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    # Medical Alerts (Vital in Dentistry before anesthesia/surgery)
    has_diabetes = models.BooleanField(default=False)
    has_hypertension = models.BooleanField(default=False)
    has_bleeding_disorder = models.BooleanField(default=False)
    has_cardiac_condition = models.BooleanField(default=False)
    has_asthma = models.BooleanField(default=False)
    is_pregnant = models.BooleanField(default=False)
    has_allergies = models.BooleanField(default=False)
    allergy_details = models.CharField(max_length=255, blank=True, null=True,
                                      help_text="e.g. Penicillin, Latex, NSAIDs, Local Anesthetic")
    current_medications = models.TextField(blank=True, null=True, help_text="e.g. Blood thinners, Aspirin, Insulin")
    medical_history_notes = models.TextField(blank=True, null=True)

    # Visual Dental Odontogram State (React-Advanced-Odontogram)
    odontogram_state = models.JSONField(default=dict, blank=True, null=True,
                                        help_text="Full React Advanced Odontogram chart JSON state")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def get_active_medical_alerts(self):
        alerts = []
        if self.has_diabetes: alerts.append("Diabetes")
        if self.has_hypertension: alerts.append("Hypertension")
        if self.has_bleeding_disorder: alerts.append("Bleeding Disorder (Caution)")
        if self.has_cardiac_condition: alerts.append("Cardiac Condition")
        if self.has_asthma: alerts.append("Asthma")
        if self.is_pregnant: alerts.append("Pregnancy")
        if self.has_allergies and self.allergy_details:
            alerts.append(f"Allergy: {self.allergy_details}")
        elif self.has_allergies:
            alerts.append("Allergies Present")
        return alerts

    def __str__(self):
        return f"{self.full_name} ({self.mrn})"


class DentalOperatory(models.Model):
    name = models.CharField(max_length=80)
    chair_number = models.PositiveIntegerField(unique=True)
    specialty_focus = models.CharField(max_length=100, default="General Dentistry")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Chair {self.chair_number} - {self.name}"


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In (OPD Queue)'),
        ('IN_CHAIR', 'In Chair / In Treatment'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DENTIST'}, related_name='dentist_appointments')
    chair = models.ForeignKey(DentalOperatory, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)
    reason = models.CharField(max_length=255, help_text="e.g. Toothache, Scaling, Root Canal Sitting 2, Crown Fitting")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'start_time']

    def __str__(self):
        return f"{self.patient.full_name} with Dr. {self.dentist.get_full_name() or self.dentist.username} on {self.appointment_date} at {self.start_time}"


class ToothRecord(models.Model):
    TOOTH_STATUS_CHOICES = [
        ('HEALTHY', 'Healthy / Sound'),
        ('CARIES', 'Dental Caries / Decay'),
        ('FILLED', 'Restored / Filled'),
        ('RCT', 'Root Canal Treated (RCT)'),
        ('CROWN', 'Crown / Cap'),
        ('IMPLANT', 'Dental Implant'),
        ('MISSING', 'Missing / Extracted'),
        ('IMPACTED', 'Impacted (Wisdom Tooth)'),
        ('FRACTURED', 'Fractured / Broken'),
        ('VENEER', 'Aesthetic Veneer'),
        ('BRIDGE', 'Bridge Pontic / Abutment'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='tooth_records')
    tooth_number = models.IntegerField(help_text="FDI notation: 11-48 for Adult, 51-85 for Pediatric")
    is_pediatric = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=TOOTH_STATUS_CHOICES, default='HEALTHY')

    # Tooth surfaces involved (crucial for composite/amalgams)
    mesial = models.BooleanField(default=False, verbose_name="Mesial (M)")
    distal = models.BooleanField(default=False, verbose_name="Distal (D)")
    occlusal = models.BooleanField(default=False, verbose_name="Occlusal/Incisal (O/I)")
    buccal = models.BooleanField(default=False, verbose_name="Buccal/Facial (B)")
    lingual = models.BooleanField(default=False, verbose_name="Lingual/Palatal (L)")

    # Periodontal evaluation
    pocket_depth_mm = models.PositiveSmallIntegerField(default=2, help_text="Probing pocket depth in mm (1-10)")
    mobility = models.PositiveSmallIntegerField(default=0, help_text="Grade: 0=None, 1=Slight, 2=Moderate, 3=Severe")
    bleeding_on_probing = models.BooleanField(default=False)
    plaque_present = models.BooleanField(default=False)
    calculus_present = models.BooleanField(default=False)

    clinical_notes = models.TextField(blank=True, null=True)
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('patient', 'tooth_number')
        ordering = ['tooth_number']

    @property
    def surfaces_display(self):
        surfs = []
        if self.mesial: surfs.append('M')
        if self.occlusal: surfs.append('O')
        if self.distal: surfs.append('D')
        if self.buccal: surfs.append('B')
        if self.lingual: surfs.append('L')
        return "".join(surfs) if surfs else "None"

    def __str__(self):
        return f"Tooth #{self.tooth_number} - {self.get_status_display()} ({self.patient.full_name})"


class ClinicalVisit(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='clinical_visits')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DENTIST'}, related_name='conducted_visits')
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='clinical_visit')
    visit_date = models.DateField(default=timezone.now)

    chief_complaint = models.TextField(help_text="Patient's primary complaint in their own words")
    history_of_illness = models.TextField(blank=True, null=True)

    # Dental Vitals
    blood_pressure = models.CharField(max_length=20, blank=True, null=True, help_text="e.g. 120/80 mmHg")
    pulse_rate = models.PositiveIntegerField(blank=True, null=True, help_text="bpm")
    blood_sugar = models.CharField(max_length=30, blank=True, null=True, help_text="e.g. Fasting 110 mg/dL")

    # SOAP Clinical Notes
    subjective = models.TextField(blank=True, null=True, help_text="Symptoms, pain duration, sensitivity triggers (cold/hot/sweet)")
    objective = models.TextField(blank=True, null=True, help_text="Intra-oral examination, percussion tenderness, soft tissue, lymph nodes")
    assessment = models.TextField(help_text="Clinical diagnosis (e.g. Acute Pulpitis i.r.t 36, Dental Caries i.r.t 11, 21)")
    treatment_plan = models.TextField(help_text="Proposed clinical action plan & procedures")

    next_recall_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date', '-created_at']

    def __str__(self):
        return f"Visit {self.visit_date} - {self.patient.full_name} by Dr. {self.dentist.get_full_name() or self.dentist.username}"


class ProcedureCatalog(models.Model):
    CATEGORY_CHOICES = [
        ('DIAGNOSTIC', 'Diagnostic & Radiography'),
        ('PREVENTIVE', 'Preventive & Hygiene (Scaling)'),
        ('RESTORATIVE', 'Restorative / Fillings'),
        ('ENDODONTIC', 'Endodontics (Root Canal Treatment)'),
        ('PERIODONTIC', 'Periodontics & Gum Surgery'),
        ('PROSTHODONTIC', 'Prosthodontics (Crowns, Bridges, Dentures)'),
        ('ORAL_SURGERY', 'Oral & Maxillofacial Surgery'),
        ('IMPLANT', 'Dental Implantology'),
        ('ORTHODONTIC', 'Orthodontics & Aligners'),
        ('COSMETIC', 'Cosmetic & Aesthetic Dentistry'),
    ]

    code = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    standard_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"[{self.code}] {self.name} - ₹{self.standard_fee}"


class TreatmentItem(models.Model):
    STATUS_CHOICES = [
        ('PLANNED', 'Planned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='treatment_items')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DENTIST'}, related_name='treatments_performed')
    procedure = models.ForeignKey(ProcedureCatalog, on_delete=models.CASCADE)
    tooth_number = models.CharField(max_length=50, blank=True, null=True,
                                   help_text="e.g. 16, or 'Upper Arch', 'Full Mouth'")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True, null=True)
    planned_date = models.DateField(default=timezone.now)
    completed_date = models.DateTimeField(blank=True, null=True)

    @property
    def net_cost(self):
        return max(Decimal('0.00'), self.cost - self.discount)

    def __str__(self):
        return f"{self.procedure.name} ({self.tooth_number or 'General'}) - {self.status}"


class DentalLabOrder(models.Model):
    WORK_TYPE_CHOICES = [
        ('ZIRCONIA_CROWN', 'Zirconia Crown (Monolithic/Layered)'),
        ('PFM_CROWN', 'PFM (Porcelain Fused to Metal) Crown'),
        ('EMAX_CROWN', 'E-Max Ceramic Crown / Veneer'),
        ('COMPLETE_DENTURE', 'Complete Denture (High Impact Acrylic)'),
        ('CAST_PARTIAL', 'Cast Partial Denture (Cobalt-Chrome)'),
        ('CLEAR_ALIGNER', 'Clear Aligner Set'),
        ('NIGHTGUARD', 'Occlusal Splint / Nightguard'),
        ('IMPLANT_ABUTMENT', 'Custom Implant Abutment + Crown'),
        ('STUDY_MODEL', 'Study Model / Orthodontic Cast'),
    ]

    STATUS_CHOICES = [
        ('IMPRESSION_SENT', 'Impression / Scan Sent to Lab'),
        ('IN_FABRICATION', 'In Lab Fabrication'),
        ('RECEIVED', 'Received at Clinic (Ready for Trial/Fitting)'),
        ('FITTED_OK', 'Fitted & Cemented (Case Closed)'),
        ('REVISION_REQUIRED', 'Sent Back for Remake / Shade Revision'),
    ]

    order_number = models.CharField(max_length=30, unique=True)
    lab_name = models.CharField(max_length=120, help_text="Dental Craft / Apex Dental Lab")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='lab_orders')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DENTIST'})
    teeth_numbers = models.CharField(max_length=50, help_text="e.g. 11, 21 or 46")
    work_type = models.CharField(max_length=30, choices=WORK_TYPE_CHOICES)
    shade = models.CharField(max_length=50, help_text="e.g. VITA A2, A3.5, Bleach BL2, Stump shade ST4")
    sent_date = models.DateField(default=timezone.now)
    expected_delivery = models.DateField()
    received_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='IMPRESSION_SENT')
    lab_charges = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    instructions = models.TextField(blank=True, null=True, help_text="Margin design, contact tightness, occlusion instructions")

    class Meta:
        ordering = ['-sent_date']

    def __str__(self):
        return f"{self.order_number} - {self.get_work_type_display()} for {self.patient.full_name}"


class DentalRadiograph(models.Model):
    TYPE_CHOICES = [
        ('IOPA', 'IOPA (Intraoral Periapical X-Ray)'),
        ('OPG', 'OPG (Orthopantomogram / Full Panoramic)'),
        ('BITEWING', 'Bitewing Radiograph'),
        ('CBCT', 'CBCT 3D Scan Slice'),
        ('INTRAORAL_PHOTO', 'Intraoral Camera Photo'),
        ('SMILE_PHOTO', 'Clinical Extraoral / Smile Photo'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='radiographs')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DENTIST'})
    image_type = models.CharField(max_length=25, choices=TYPE_CHOICES, default='IOPA')
    tooth_number = models.CharField(max_length=30, blank=True, null=True, help_text="e.g. 36, 11-21")
    image_file = models.ImageField(upload_to='radiographs/')
    findings = models.TextField(blank=True, null=True, help_text="Radiographic findings: periapical radiolucency, bone resorption, canal calcification")
    captured_date = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-captured_date']

    def __str__(self):
        return f"{self.get_image_type_display()} - {self.patient.full_name} ({self.tooth_number or 'Full'})"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    dentist = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'DENTIST'}, related_name='prescriptions_written')
    clinical_visit = models.ForeignKey(ClinicalVisit, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    prescription_date = models.DateField(default=timezone.now)
    general_advice = models.TextField(blank=True, null=True,
                                     help_text="Warm saline rinses, soft diet, avoid hot food on operative side")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-prescription_date', '-created_at']

    def __str__(self):
        return f"Rx #{self.id} for {self.patient.full_name} on {self.prescription_date}"


class PrescriptionItem(models.Model):
    FORM_CHOICES = [
        ('TABLET', 'Tablet (Tab)'),
        ('CAPSULE', 'Capsule (Cap)'),
        ('SYRUP', 'Syrup / Suspension'),
        ('MOUTHWASH', 'Mouthwash / Oral Rinse'),
        ('GEL', 'Oral Gel / Ointment'),
        ('INJECTION', 'Injection'),
    ]

    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=120, help_text="e.g. Augmentin 625mg, Zerodol-SP, Metrogyl 400mg")
    form = models.CharField(max_length=20, choices=FORM_CHOICES, default='TABLET')
    dosage = models.CharField(max_length=50, default="1 Tablet")
    frequency = models.CharField(max_length=80, help_text="e.g. TDS (3 times/day), BD (Twice daily), OD (Once daily), SOS (When needed)")
    duration = models.CharField(max_length=50, help_text="e.g. 5 days, 3 days")
    instructions = models.CharField(max_length=150, default="After food",
                                   help_text="e.g. After food, Avoid drinking water for 30 min after application")

    def __str__(self):
        return f"{self.medicine_name} - {self.frequency} x {self.duration}"


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending / Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Fully Paid'),
        ('REFUNDED', 'Refunded'),
    ]

    invoice_number = models.CharField(max_length=30, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='invoices')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    invoice_date = models.DateField(default=timezone.now)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    net_payable = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    balance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-invoice_date', '-created_at']

    def update_totals(self):
        items_total = sum(item.total_price for item in self.items.all()) if self.pk else Decimal('0.00')
        self.total_amount = items_total
        self.net_payable = max(Decimal('0.00'), (self.total_amount - self.discount_amount) + self.tax_amount)
        total_paid = sum(pay.amount for pay in self.payments.all()) if self.pk else Decimal('0.00')
        self.paid_amount = total_paid
        self.balance_amount = max(Decimal('0.00'), self.net_payable - self.paid_amount)
        if self.paid_amount >= self.net_payable and self.net_payable > 0:
            self.status = 'PAID'
        elif self.paid_amount > 0:
            self.status = 'PARTIAL'
        else:
            self.status = 'PENDING'
        self.save()

    def __str__(self):
        return f"{self.invoice_number} - {self.patient.full_name} (₹{self.net_payable})"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    treatment_item = models.ForeignKey(TreatmentItem, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x{self.quantity}"


class Payment(models.Model):
    METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('UPI', 'UPI (GPay / PhonePe / Paytm / QR)'),
        ('CARD', 'Debit / Credit Card'),
        ('NETBANKING', 'Net Banking / NEFT'),
        ('INSURANCE', 'Dental Insurance / TPA'),
    ]

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='UPI')
    transaction_reference = models.CharField(max_length=100, blank=True, null=True,
                                           help_text="UPI UTR number or Card auth code")
    payment_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    notes = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Payment ₹{self.amount} ({self.get_payment_method_display()}) for {self.invoice.invoice_number}"


class DentalMaterialInventory(models.Model):
    CATEGORY_CHOICES = [
        ('ANESTHESIA', 'Local Anesthetics & Needles'),
        ('COMPOSITE', 'Composites & Bonding Agents'),
        ('ENDODONTICS', 'Endodontic Files & Sealers'),
        ('IMPRESSION', 'Impression Materials (Alginate/Putty)'),
        ('PROSTHETICS', 'Cements & Acrylics'),
        ('SURGICAL', 'Sutures, Blades & Hemostats'),
        ('INFECTION_CONTROL', 'Sterilization, Pouches, Autoclave Strips'),
        ('DISPOSABLES', 'Gloves, Masks, Bibs, Suction Tips'),
    ]

    item_code = models.CharField(max_length=40, unique=True)
    name = models.CharField(max_length=150)
    category = models.CharField(max_length=25, choices=CATEGORY_CHOICES)
    current_stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=30, default="Boxes", help_text="e.g. Cartridges, Syringes, Bottles, Boxes")
    reorder_threshold = models.IntegerField(default=10)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    supplier_name = models.CharField(max_length=120, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    @property
    def is_low_stock(self):
        return self.current_stock <= self.reorder_threshold

    def __str__(self):
        return f"{self.name} ({self.current_stock} {self.unit})"
