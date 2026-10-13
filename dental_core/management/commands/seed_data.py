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
    help = 'Seeds initial users, dental catalog, operatories, materials, and ensures patient tables are clean for fresh start.'

    def handle(self, *args, **options):
        self.stdout.write("Initializing RK Hospital Bawaskar system...")

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
        # Primary Hospital Administrator (User requested: username='admin', password='Anurag@268724')
        admin_user, _ = User.objects.get_or_create(username='admin', defaults={
            'first_name': 'Admin',
            'last_name': 'Bawaskar',
            'email': 'admin@rkhospital.com',
            'role': 'ADMIN',
            'specialization': 'Medical Director & Chief Administrator',
            'qualification': 'MDS, Oral & Maxillofacial Surgery',
            'license_number': 'MH-DC-44210',
            'phone_number': '+91 98220 11223',
            'is_staff': True,
            'is_superuser': True,
        })
        admin_user.set_password('Anurag@268724')
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'Bawaskar'
        admin_user.role = 'ADMIN'
        admin_user.is_staff = True
        admin_user.is_superuser = True
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

        for code, name, cat, fee, desc in procedures_data:
            ProcedureCatalog.objects.get_or_create(
                code=code,
                defaults={'name': name, 'category': cat, 'standard_fee': fee, 'description': desc, 'is_active': True}
            )

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

        # 5. Clean Fresh Start: Keep all Patient and Clinical Case records 100% empty
        Patient.objects.all().delete()
        Appointment.objects.all().delete()
        ToothRecord.objects.all().delete()
        ClinicalVisit.objects.all().delete()
        TreatmentItem.objects.all().delete()
        DentalLabOrder.objects.all().delete()
        DentalRadiograph.objects.all().delete()
        Prescription.objects.all().delete()
        PrescriptionItem.objects.all().delete()
        Invoice.objects.all().delete()
        InvoiceItem.objects.all().delete()
        Payment.objects.all().delete()

        # Delete any dummy demo patient user
        User.objects.filter(username__in=['patient.raj', 'patient']).delete()

        self.stdout.write(self.style.SUCCESS("RK Hospital Bawaskar system ready: Procedure Catalog, Operatory Chairs & Inventory active."))
        self.stdout.write(self.style.SUCCESS("All patient tables are 100% CLEAN and FRESH (0 patients)."))
        self.stdout.write(self.style.SUCCESS("Primary Admin credentials active: username='admin' | password='Anurag@268724'"))
