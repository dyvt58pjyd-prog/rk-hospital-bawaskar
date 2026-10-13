import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from dental_core.models import (
    User, Patient, DentalOperatory, ProcedureCatalog,
    Appointment, ToothRecord, ClinicalVisit, TreatmentItem,
    DentalLabOrder, DentalRadiograph, Prescription, PrescriptionItem,
    Invoice, InvoiceItem, Payment, DentalMaterialInventory
)


class Command(BaseCommand):
    help = 'Seeds initial users, dental catalog, operatories, demo patients, dental charts, appointments, and billing data.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding RK Hospital Bawaskar system data...")

        # 1. Operatories / Dental Chairs
        chair1, _ = DentalOperatory.objects.get_or_create(
            chair_number=1,
            defaults={'name': 'Operatory A - Conservative & Micro-Endo', 'specialty_focus': 'Endodontics & Restorative', 'is_active': True}
        )
        chair2, _ = DentalOperatory.objects.get_or_create(
            chair_number=2,
            defaults={'name': 'Operatory B - Surgical Suite & Implants', 'specialty_focus': 'Oral Surgery & Implantology', 'is_active': True}
        )
        chair3, _ = DentalOperatory.objects.get_or_create(
            chair_number=3,
            defaults={'name': 'Operatory C - Orthodontics & Aesthetics', 'specialty_focus': 'Orthodontics & Clear Aligners', 'is_active': True}
        )
        chair4, _ = DentalOperatory.objects.get_or_create(
            chair_number=4,
            defaults={'name': 'Operatory D - Hygiene & Preventive Care', 'specialty_focus': 'Periodontics & Oral Prophylaxis', 'is_active': True}
        )

        # 2. Roles & Users
        # Admin / Medical Director
        admin_user, created = User.objects.get_or_create(username='dr.bawaskar', defaults={
            'first_name': 'Dr. R.K.',
            'last_name': 'Bawaskar',
            'email': 'dr.bawaskar@rkhospital.com',
            'role': 'ADMIN',
            'specialization': 'Maxillofacial Surgeon & Implantologist',
            'qualification': 'MDS, FIBOMS, Fellow ITI (Switzerland)',
            'license_number': 'MH-DC-44210',
            'phone_number': '+91 98220 11223',
            'is_staff': True,
            'is_superuser': True,
        })
        if created:
            admin_user.set_password('admin123')
            admin_user.save()

        # Dentist 1 (Endodontist)
        dentist1, created = User.objects.get_or_create(username='dr.sharma', defaults={
            'first_name': 'Dr. Priya',
            'last_name': 'Sharma',
            'email': 'priya.sharma@rkhospital.com',
            'role': 'DENTIST',
            'specialization': 'Endodontist & Conservative Dentist',
            'qualification': 'BDS, MDS (Conservative Dentistry)',
            'license_number': 'MH-DC-51204',
            'phone_number': '+91 98220 44556',
            'is_staff': True,
        })
        if created:
            dentist1.set_password('dentist123')
            dentist1.save()

        # Dentist 2 (Orthodontist)
        dentist2, created = User.objects.get_or_create(username='dr.kapoor', defaults={
            'first_name': 'Dr. Rohan',
            'last_name': 'Kapoor',
            'email': 'rohan.kapoor@rkhospital.com',
            'role': 'DENTIST',
            'specialization': 'Orthodontist & Dentofacial Orthopedics',
            'qualification': 'BDS, MDS (Orthodontics)',
            'license_number': 'MH-DC-48992',
            'phone_number': '+91 98220 77889',
            'is_staff': True,
        })
        if created:
            dentist2.set_password('dentist123')
            dentist2.save()

        # Receptionist
        receptionist, created = User.objects.get_or_create(username='reception', defaults={
            'first_name': 'Sneha',
            'last_name': 'Verma',
            'email': 'reception@rkhospital.com',
            'role': 'RECEPTIONIST',
            'phone_number': '+91 98220 99001',
            'is_staff': True,
        })
        if created:
            receptionist.set_password('reception123')
            receptionist.save()

        # Dental Hygienist
        hygienist, created = User.objects.get_or_create(username='hygienist', defaults={
            'first_name': 'Pooja',
            'last_name': 'Shinde',
            'email': 'pooja.hygiene@rkhospital.com',
            'role': 'HYGIENIST',
            'phone_number': '+91 98220 33445',
            'is_staff': True,
        })
        if created:
            hygienist.set_password('hygienist123')
            hygienist.save()

        # Pharmacist / Inventory
        pharmacist, created = User.objects.get_or_create(username='pharmacy', defaults={
            'first_name': 'Amit',
            'last_name': 'Deshmukh',
            'email': 'store@rkhospital.com',
            'role': 'PHARMACIST',
            'phone_number': '+91 98220 55667',
            'is_staff': True,
        })
        if created:
            pharmacist.set_password('pharmacy123')
            pharmacist.save()

        # Patient Portal User
        patient_user, created = User.objects.get_or_create(username='patient.raj', defaults={
            'first_name': 'Rajesh',
            'last_name': 'Malhotra',
            'email': 'rajesh.malhotra@gmail.com',
            'role': 'PATIENT',
            'phone_number': '+91 98111 22334',
        })
        if created:
            patient_user.set_password('patient123')
            patient_user.save()

        # 3. Procedure Catalog
        procedures_data = [
            # Diagnostic
            ('D-001', 'Comprehensive Dental Examination & Consultation', 'DIAGNOSTIC', Decimal('500.00'), 'Full intra-oral examination and treatment planning'),
            ('D-002', 'Digital Intraoral Periapical (IOPA) X-Ray', 'DIAGNOSTIC', Decimal('300.00'), 'High-resolution digital sensor radiograph'),
            ('D-003', 'Full Mouth Digital OPG (Panoramic Radiograph)', 'DIAGNOSTIC', Decimal('900.00'), 'Full panoramic extra-oral radiograph'),
            # Preventive
            ('P-101', 'Full Mouth Scaling & Ultrasonic Polishing', 'PREVENTIVE', Decimal('1500.00'), 'Removal of supragingival & subgingival calculus, stains'),
            ('P-102', 'Deep Scaling & Root Planing (Per Quadrant)', 'PERIODONTIC', Decimal('1200.00'), 'Subgingival debridement and curettage under local anesthesia'),
            ('P-103', 'Topical Fluoride Application (Pediatric)', 'PREVENTIVE', Decimal('800.00'), 'Enamel remineralization & caries prevention'),
            # Restorative
            ('R-201', 'Tooth-Colored Light Cure Composite Restoration (Class I)', 'RESTORATIVE', Decimal('1200.00'), 'Nano-hybrid composite resin restoration'),
            ('R-202', 'Tooth-Colored Light Cure Composite Restoration (Class II)', 'RESTORATIVE', Decimal('1800.00'), 'Multi-surface composite with sectional matrix band'),
            ('R-203', 'Glass Ionomer Cement (GIC) Restoration', 'RESTORATIVE', Decimal('900.00'), 'Fluoride-releasing biocompatible restoration'),
            # Endodontics
            ('E-301', 'Single-Sitting Rotary Root Canal Treatment (Anterior)', 'ENDODONTIC', Decimal('3500.00'), 'Apex locator & rotary NiTi biomechanical prep, gutta-percha obturation'),
            ('E-302', 'Root Canal Treatment - Premolar / Molar', 'ENDODONTIC', Decimal('4500.00'), 'Multi-canal treatment with electronic length determination'),
            ('E-303', 'Fiber Post & Core Build-Up', 'ENDODONTIC', Decimal('1800.00'), 'Glass fiber post cementation and composite core reconstruction'),
            # Prosthodontics
            ('PR-401', 'High-Translucency Multi-Layered Zirconia Crown', 'PROSTHODONTIC', Decimal('8500.00'), 'CAD/CAM milled aesthetic monolithic zirconia crown (10-yr warranty)'),
            ('PR-402', 'Porcelain Fused to Metal (PFM) Crown (DMLS / Laser Sintered)', 'PROSTHODONTIC', Decimal('4000.00'), 'Precision laser-sintered ceramic-metal crown'),
            ('PR-403', 'E-Max Lithium Disilicate Aesthetic Veneer / Crown', 'COSMETIC', Decimal('10000.00'), 'Supreme anterior aesthetic ceramic veneer'),
            ('PR-404', 'Complete Denture (BPS Precision System - Both Arches)', 'PROSTHODONTIC', Decimal('28000.00'), 'Biofunctional prosthetic system high-density dentures'),
            # Oral Surgery
            ('OS-501', 'Simple Non-Surgical Tooth Extraction', 'ORAL_SURGERY', Decimal('800.00'), 'Atraumatic forceps removal with local anesthesia'),
            ('OS-502', 'Surgical Disimpaction (Impacted 3rd Molar Wisdom Tooth)', 'ORAL_SURGERY', Decimal('4500.00'), 'Flap reflection, bone guttering, tooth sectioning and suture'),
            # Implants
            ('I-601', 'Titanium Dental Implant (Osseointegrated Root Form)', 'IMPLANT', Decimal('25000.00'), 'Surgical implant fixture placement (Grade 4/5 Titanium)'),
            ('I-602', 'Bone Grafting & Collagen Membrane (GBR)', 'IMPLANT', Decimal('12000.00'), 'Bio-Oss xenograft + Bio-Gide resorbable membrane'),
            # Orthodontics & Cosmetic
            ('OR-701', 'Clear Aligners Full Case (Comprehensive Alignment)', 'ORTHODONTIC', Decimal('65000.00'), 'Custom 3D staged transparent aligners treatment'),
            ('C-801', 'In-Office Laser Teeth Whitening (Power Bleaching)', 'COSMETIC', Decimal('8000.00'), '35% Hydrogen Peroxide light-activated bleaching (3 cycles)'),
        ]

        catalog_objs = {}
        for code, name, cat, fee, desc in procedures_data:
            proc, _ = ProcedureCatalog.objects.get_or_create(
                code=code,
                defaults={'name': name, 'category': cat, 'standard_fee': fee, 'description': desc, 'is_active': True}
            )
            catalog_objs[code] = proc

        # 4. Inventory Items
        inventory_data = [
            ('MAT-001', 'Septodont Lignospan Special (2% Lignocaine + Adrenaline 1:80000)', 'ANESTHESIA', 45, 'Boxes (50 Cartridges)', 15, Decimal('1450.00'), 'Septodont India'),
            ('MAT-002', 'Septoject Dental Needles 30G Short', 'ANESTHESIA', 60, 'Boxes (100 pcs)', 20, Decimal('380.00'), 'Septodont India'),
            ('MAT-003', '3M Filtek Z250 Universal Composite Syringe (Shade A2)', 'COMPOSITE', 18, 'Syringes (4g)', 5, Decimal('1250.00'), '3M Health Care'),
            ('MAT-004', '3M Single Bond Universal Adhesive 5ml', 'COMPOSITE', 12, 'Bottles (5ml)', 4, Decimal('2100.00'), '3M Health Care'),
            ('MAT-005', 'Dentsply Protaper Gold Rotary Files (SX-F3 Assorted 25mm)', 'ENDODONTICS', 24, 'Packs (6 files)', 8, Decimal('2400.00'), 'Dentsply Sirona'),
            ('MAT-006', 'AH Plus Resin-Based Root Canal Sealer', 'ENDODONTICS', 10, 'Packs', 3, Decimal('2800.00'), 'Dentsply Sirona'),
            ('MAT-007', 'Cavex ColorChange Dust-free Dental Alginate 500g', 'IMPRESSION', 35, 'Packs (500g)', 10, Decimal('550.00'), 'Cavex Holland'),
            ('MAT-008', 'Aquasil Ultra Soft Putty (Base + Catalyst)', 'IMPRESSION', 14, 'Tubs', 4, Decimal('3600.00'), 'Dentsply Sirona'),
            ('MAT-009', 'RelyX U200 Self-Adhesive Resin Cement Automix (A2)', 'PROSTHETICS', 8, 'Syringes (8.5g)', 3, Decimal('4200.00'), '3M Health Care'),
            ('MAT-010', 'Ethicon Ethilon 3-0 Black Monofilament Nylon Suture', 'SURGICAL', 28, 'Boxes (12 foils)', 10, Decimal('980.00'), 'Johnson & Johnson'),
            ('MAT-011', 'Sterilization Self-Sealing Pouches (90x230mm)', 'INFECTION_CONTROL', 85, 'Boxes (200 pcs)', 20, Decimal('650.00'), 'Medipack'),
            ('MAT-012', 'Nitrile Medical Examination Gloves (Powder-Free, Medium)', 'DISPOSABLES', 8, 'Boxes (100 pcs)', 15, Decimal('450.00'), 'CarePlus (Low Stock Alert)'),
        ]

        for sku, name, cat, stock, unit, threshold, cost, supplier in inventory_data:
            DentalMaterialInventory.objects.get_or_create(
                item_code=sku,
                defaults={
                    'name': name, 'category': cat, 'current_stock': stock,
                    'unit': unit, 'reorder_threshold': threshold, 'unit_cost': cost,
                    'supplier_name': supplier, 'expiry_date': timezone.now().date() + datetime.timedelta(days=365)
                }
            )

        # 5. Demo Patients
        # Patient 1: Rajesh Malhotra (Has web login)
        p1, _ = Patient.objects.get_or_create(
            mrn='RKH-2026-0001',
            defaults={
                'user': patient_user,
                'first_name': 'Rajesh',
                'last_name': 'Malhotra',
                'phone': '+91 98111 22334',
                'email': 'rajesh.malhotra@gmail.com',
                'date_of_birth': datetime.date(1986, 5, 14),
                'gender': 'M',
                'blood_group': 'B+',
                'address': 'Flat 402, Royal Residency, Pune - 411038',
                'emergency_contact_name': 'Sunita Malhotra (Wife)',
                'emergency_contact_phone': '+91 98111 55667',
                'has_diabetes': True,
                'has_hypertension': False,
                'has_allergies': True,
                'allergy_details': 'Penicillin (Severe Rash/Urticaria)',
                'current_medications': 'Metformin 500mg BD for Type 2 DM',
                'medical_history_notes': 'HbA1c: 6.8% checked 2 months ago. Avoid Penicillin/Amoxicillin.',
            }
        )

        # Patient 2: Sunita Deshpande
        p2, _ = Patient.objects.get_or_create(
            mrn='RKH-2026-0002',
            defaults={
                'first_name': 'Sunita',
                'last_name': 'Deshpande',
                'phone': '+91 94220 88990',
                'email': 'sunita.deshpande@outlook.com',
                'date_of_birth': datetime.date(1992, 11, 20),
                'gender': 'F',
                'blood_group': 'O+',
                'address': 'Plot 15, Green Acres, Aundh, Pune',
                'emergency_contact_name': 'Nikhil Deshpande',
                'emergency_contact_phone': '+91 94220 11223',
                'has_cardiac_condition': False,
                'has_asthma': False,
                'is_pregnant': False,
                'has_allergies': False,
                'medical_history_notes': 'No known systemic illnesses.',
            }
        )

        # Patient 3: Anil Kulkarni (Senior citizen, Hypertension + Cardiac)
        p3, _ = Patient.objects.get_or_create(
            mrn='RKH-2026-0003',
            defaults={
                'first_name': 'Anil',
                'last_name': 'Kulkarni',
                'phone': '+91 98900 12345',
                'email': 'kulkarni.anil@yahoo.co.in',
                'date_of_birth': datetime.date(1960, 3, 10),
                'gender': 'M',
                'blood_group': 'A+',
                'address': 'Shubham Heights, Kothrud, Pune',
                'emergency_contact_name': 'Sachin Kulkarni (Son)',
                'emergency_contact_phone': '+91 98900 67890',
                'has_hypertension': True,
                'has_cardiac_condition': True,
                'has_bleeding_disorder': False,
                'current_medications': 'Telmisartan 40mg OD, Ecosprin 75mg OD (Blood thinner)',
                'medical_history_notes': 'Ecosprin stopped in consultation with cardiologist before surgical extraction.',
            }
        )

        # Patient 4: Ananya Patil (Pediatric / Orthodontic)
        p4, _ = Patient.objects.get_or_create(
            mrn='RKH-2026-0004',
            defaults={
                'first_name': 'Ananya',
                'last_name': 'Patil',
                'phone': '+91 97654 32100',
                'email': 'patil.parent@gmail.com',
                'date_of_birth': datetime.date(2012, 8, 15),
                'gender': 'F',
                'blood_group': 'AB+',
                'address': 'Silver Crest, Baner, Pune',
                'emergency_contact_name': 'Mahesh Patil (Father)',
                'emergency_contact_phone': '+91 97654 32100',
                'has_asthma': True,
                'medical_history_notes': 'Mild seasonal asthma, carries Salbutamol inhaler.',
            }
        )

        # 6. Odontogram / Tooth Records for Patient 1 (Rajesh Malhotra)
        # FDI teeth standard 32 adult teeth
        # Tooth 16: Caries on Occlusal + Mesial
        # Tooth 26: Root Canal Treated + Crown Planned
        # Tooth 36: Full Crown
        # Tooth 46: Filled (Composite)
        # Tooth 18, 28: Missing / Extracted
        # Tooth 38, 48: Impacted
        teeth_statuses_p1 = {
            16: ('CARIES', True, False, True, False, False, "Deep dentinal caries encroaching pulp. Sensitive to cold."),
            26: ('RCT', False, False, True, False, False, "Completed 3 canals obturation. Advised Zirconia Crown."),
            36: ('CROWN', False, False, False, False, False, "PFM crown fitted 2 years ago, margins healthy."),
            46: ('FILLED', False, True, True, False, False, "MOD Composite restoration intact."),
            18: ('MISSING', False, False, False, False, False, "Extracted 5 years ago."),
            28: ('MISSING', False, False, False, False, False, "Congenitally missing / extracted."),
            38: ('IMPACTED', False, False, False, False, False, "Mesioangular impaction, pericoronitis episodes."),
            48: ('IMPACTED', False, False, False, False, False, "Vertical impaction."),
            11: ('HEALTHY', False, False, False, False, False, "Sound tooth structure."),
            21: ('HEALTHY', False, False, False, False, False, "Sound tooth structure."),
        }

        for t_num in range(11, 49):
            if t_num % 10 in [9, 0]: continue # valid FDI only has 1-8 per quadrant
            status_info = teeth_statuses_p1.get(t_num, ('HEALTHY', False, False, False, False, False, ""))
            status, m, d, o, b, l, notes = status_info
            ToothRecord.objects.update_or_create(
                patient=p1,
                tooth_number=t_num,
                defaults={
                    'status': status,
                    'mesial': m,
                    'distal': d,
                    'occlusal': o,
                    'buccal': b,
                    'lingual': l,
                    'pocket_depth_mm': 4 if t_num == 38 else 2,
                    'clinical_notes': notes,
                    'last_updated_by': admin_user,
                }
            )

        # 7. Appointments for Today & Tomorrow
        today = timezone.now().date()
        Appointment.objects.get_or_create(
            patient=p1,
            dentist=dentist1,
            appointment_date=today,
            start_time=datetime.time(10, 30),
            defaults={
                'chair': chair1,
                'end_time': datetime.time(11, 15),
                'reason': 'Sitting 2: RCT Biomechanical Prep & Obturation i.r.t 26',
                'status': 'IN_CHAIR',
                'notes': 'Allergic to Penicillin - prescribed Cefixime instead.'
            }
        )

        Appointment.objects.get_or_create(
            patient=p2,
            dentist=dentist1,
            appointment_date=today,
            start_time=datetime.time(11, 30),
            defaults={
                'chair': chair4,
                'end_time': datetime.time(12, 15),
                'reason': 'Full Mouth Ultrasonic Scaling & Stain Removal',
                'status': 'CHECKED_IN',
                'notes': 'Patient arrived at OPD desk, waiting in lounge.'
            }
        )

        Appointment.objects.get_or_create(
            patient=p3,
            dentist=admin_user,
            appointment_date=today,
            start_time=datetime.time(14, 0),
            defaults={
                'chair': chair2,
                'end_time': datetime.time(15, 0),
                'reason': 'Surgical Extraction of Grossly Carious 37 under Local Anesthesia',
                'status': 'CONFIRMED',
                'notes': 'Check BP before local anesthetic infiltration. Blood thinner stopped 3 days prior.'
            }
        )

        Appointment.objects.get_or_create(
            patient=p4,
            dentist=dentist2,
            appointment_date=today,
            start_time=datetime.time(16, 0),
            defaults={
                'chair': chair3,
                'end_time': datetime.time(16, 45),
                'reason': 'Clear Aligner Tray #4 Delivery & Attachment Check',
                'status': 'SCHEDULED',
                'notes': 'Review tracking on maxillary lateral incisors.'
            }
        )

        # 8. Clinical Visit with SOAP Notes for Patient 1
        visit1, _ = ClinicalVisit.objects.get_or_create(
            patient=p1,
            dentist=dentist1,
            visit_date=today,
            defaults={
                'chief_complaint': 'Severe throbbing pain in upper left back tooth on drinking cold water and chewing since 4 days.',
                'history_of_illness': 'Pain started mild a week ago, exacerbated over last 48 hours, radiating to left temporal region.',
                'blood_pressure': '124/82 mmHg',
                'pulse_rate': 74,
                'blood_sugar': 'RBS: 128 mg/dL',
                'subjective': 'Patient reports constant dull ache with acute sharp episodes provoked by temperature changes. Disturbed sleep last night.',
                'objective': 'Tooth 26 exhibits deep disto-occlusal caries. Tender to vertical percussion (+). Electric pulp test shows hypersensitive response. Soft tissues normal, no sinus tract.',
                'assessment': 'Acute Irreversible Pulpitis with symptomatic apical periodontitis i.r.t Tooth 26.',
                'treatment_plan': '1. Multi-canal Root Canal Treatment i.r.t 26 (MB1, MB2, DB, Palatal).\n2. Post-endodontic Core Build-up.\n3. Full Contour Monolithic Zirconia Crown.',
                'next_recall_date': today + datetime.timedelta(days=7),
            }
        )

        # 9. Treatments for Patient 1
        t_rct, _ = TreatmentItem.objects.get_or_create(
            patient=p1,
            procedure=catalog_objs['E-302'],
            tooth_number='26',
            defaults={
                'dentist': dentist1,
                'status': 'COMPLETED',
                'cost': Decimal('4500.00'),
                'discount': Decimal('0.00'),
                'notes': 'Canals shaped and obturated with AH Plus + 4% gutta-percha cones. Post-op X-ray satisfactory.',
                'completed_date': timezone.now()
            }
        )

        t_crown, _ = TreatmentItem.objects.get_or_create(
            patient=p1,
            procedure=catalog_objs['PR-401'],
            tooth_number='26',
            defaults={
                'dentist': dentist1,
                'status': 'IN_PROGRESS',
                'cost': Decimal('8500.00'),
                'discount': Decimal('500.00'),
                'notes': 'Tooth preparation completed, elastomeric impression taken and sent to DentCraft Lab.',
            }
        )

        # 10. Dental Lab Order for Patient 1
        lab_order, _ = DentalLabOrder.objects.get_or_create(
            order_number='LAB-2026-0042',
            defaults={
                'lab_name': 'DentCraft CAD/CAM Dental Solutions',
                'patient': p1,
                'dentist': dentist1,
                'teeth_numbers': '26',
                'work_type': 'ZIRCONIA_CROWN',
                'shade': 'VITA A2 with moderate cervical saturation',
                'sent_date': today - datetime.timedelta(days=2),
                'expected_delivery': today + datetime.timedelta(days=2),
                'status': 'IN_FABRICATION',
                'lab_charges': Decimal('2200.00'),
                'instructions': 'Chamfer finish line, tight proximal contacts, keep clearance in centric occlusion 1.5mm.',
            }
        )

        # 11. Prescription for Patient 1
        rx1, _ = Prescription.objects.get_or_create(
            patient=p1,
            dentist=dentist1,
            clinical_visit=visit1,
            defaults={
                'prescription_date': today,
                'general_advice': 'Avoid chewing hard food on left side until crown is cemented. Rinse mouth with lukewarm saline water 3 times a day.',
            }
        )

        PrescriptionItem.objects.get_or_create(
            prescription=rx1,
            medicine_name='Cefixime 200mg (Note: Patient Penicillin Allergic)',
            defaults={
                'form': 'TABLET',
                'dosage': '1 Tablet',
                'frequency': 'BD (Twice daily)',
                'duration': '5 days',
                'instructions': 'After breakfast and after dinner',
            }
        )
        PrescriptionItem.objects.get_or_create(
            prescription=rx1,
            medicine_name='Zerodol-SP (Aceclofenac 100mg + Paracetamol 325mg + Serratiopeptidase 15mg)',
            defaults={
                'form': 'TABLET',
                'dosage': '1 Tablet',
                'frequency': 'BD (Twice daily)',
                'duration': '3 days',
                'instructions': 'Strictly after food with full glass of water',
            }
        )
        PrescriptionItem.objects.get_or_create(
            prescription=rx1,
            medicine_name='Hexidine 0.2% Chlorhexidine Gluconate Mouthwash',
            defaults={
                'form': 'MOUTHWASH',
                'dosage': '10 ml rinse',
                'frequency': 'BD (Twice daily)',
                'duration': '7 days',
                'instructions': 'Swish vigorously for 1 minute and spit. Do not eat/drink for 30 minutes.',
            }
        )

        # 12. Billing / Invoice for Patient 1
        inv1, _ = Invoice.objects.get_or_create(
            invoice_number='INV-2026-0101',
            defaults={
                'patient': p1,
                'created_by': admin_user,
                'invoice_date': today,
                'total_amount': Decimal('13000.00'),
                'discount_amount': Decimal('500.00'),
                'tax_amount': Decimal('0.00'),
                'net_payable': Decimal('12500.00'),
                'paid_amount': Decimal('8000.00'),
                'balance_amount': Decimal('4500.00'),
                'status': 'PARTIAL',
                'notes': 'Advance paid for RCT & Zirconia Crown. Balance due on crown cementation.',
            }
        )

        InvoiceItem.objects.get_or_create(
            invoice=inv1,
            description='Root Canal Treatment - Molar (#26)',
            defaults={'treatment_item': t_rct, 'quantity': 1, 'unit_price': Decimal('4500.00'), 'total_price': Decimal('4500.00')}
        )
        InvoiceItem.objects.get_or_create(
            invoice=inv1,
            description='CAD/CAM Multi-layered Zirconia Crown (#26)',
            defaults={'treatment_item': t_crown, 'quantity': 1, 'unit_price': Decimal('8500.00'), 'total_price': Decimal('8500.00')}
        )

        Payment.objects.get_or_create(
            invoice=inv1,
            amount=Decimal('8000.00'),
            defaults={
                'payment_method': 'UPI',
                'transaction_reference': 'UPI/428919204812/HDFC',
                'payment_date': timezone.now(),
                'received_by': receptionist,
                'notes': 'Received via Google Pay'
            }
        )
        inv1.update_totals()

        self.stdout.write(self.style.SUCCESS("Successfully seeded RK Hospital Bawaskar system!"))
