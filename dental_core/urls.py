from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Patients
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/new/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/edit/', views.patient_edit, name='patient_edit'),

    # Dental EMR & Odontogram
    path('patients/<int:pk>/odontogram/', views.odontogram_studio, name='odontogram_studio'),
    path('api/odontogram/<int:patient_id>/state/', views.api_odontogram_state, name='api_odontogram_state'),
    path('api/tooth/<int:patient_id>/<int:tooth_number>/', views.api_tooth_record, name='api_tooth_record'),

    # Clinical Visits & SOAP
    path('patients/<int:patient_id>/visits/new/', views.clinical_visit_create, name='clinical_visit_create'),
    path('visits/<int:pk>/', views.clinical_visit_detail, name='clinical_visit_detail'),

    # Treatments
    path('patients/<int:patient_id>/treatments/new/', views.treatment_create, name='treatment_create'),
    path('treatments/<int:pk>/update-status/', views.treatment_update_status, name='treatment_update_status'),

    # Appointments & Queue
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/new/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/update-status/', views.appointment_update_status, name='appointment_update_status'),

    # Dental Lab Orders
    path('lab/', views.lab_list, name='lab_list'),
    path('lab/new/', views.lab_create, name='lab_create'),
    path('lab/<int:pk>/update-status/', views.lab_update_status, name='lab_update_status'),

    # Prescriptions (Rx)
    path('patients/<int:patient_id>/prescriptions/new/', views.prescription_create, name='prescription_create'),
    path('prescriptions/<int:pk>/print/', views.prescription_print, name='prescription_print'),

    # Invoices & Billing
    path('billing/', views.billing_list, name='billing_list'),
    path('patients/<int:patient_id>/invoices/new/', views.invoice_create, name='invoice_create'),
    path('billing/invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('billing/invoices/<int:pk>/pay/', views.invoice_add_payment, name='invoice_add_payment'),

    # Inventory & Store
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/new/', views.inventory_create, name='inventory_create'),
    path('inventory/<int:pk>/stock-adjust/', views.inventory_stock_adjust, name='inventory_stock_adjust'),

    # Radiographs & Radiology Hub
    path('radiographs/', views.radiograph_hub, name='radiograph_hub'),
    path('radiographs/upload/', views.radiograph_general_upload, name='radiograph_general_upload'),
    path('patients/<int:patient_id>/radiographs/upload/', views.radiograph_upload, name='radiograph_upload'),

    # Digital Informed Consent Forms
    path('patients/<int:patient_id>/consent/create/', views.consent_create, name='consent_create'),
    path('consent/<int:consent_id>/', views.consent_detail, name='consent_detail'),
    path('api/consent-template/', views.api_consent_template, name='api_consent_template'),

    # WhatsApp Notifications
    path('patients/<int:patient_id>/whatsapp/', views.whatsapp_send, name='whatsapp_send'),

    # Android Mobile Companion App
    path('mobile/', views.mobile_companion_view, name='mobile_companion'),
    path('mobile/quick-radiograph/', views.mobile_quick_radiograph, name='mobile_quick_radiograph'),

    # Cosmetic Dentistry: Before & After Smile Gallery
    path('smile-gallery/', views.smile_gallery_list, name='smile_gallery'),
    path('smile-gallery/new/', views.smile_transformation_create, name='smile_transformation_create'),
    path('patients/<int:patient_id>/smile-gallery/new/', views.smile_transformation_create, name='patient_smile_transformation_create'),

    # Executive Analytics & Financial Hub
    path('analytics/', views.analytics_dashboard_view, name='analytics_dashboard'),

    # OPD Kiosk & Patient Self Check-in
    path('kiosk/', views.kiosk_self_checkin, name='kiosk_self_checkin'),
    path('kiosk/poster/', views.kiosk_qr_poster, name='kiosk_qr_poster'),

    # REST API v1 Endpoints (Android App / Flutter / Web Clients)
    path('api/v1/appointments/', views.api_v1_appointments, name='api_v1_appointments'),
    path('api/v1/appointments/<int:pk>/', views.api_v1_appointment_detail, name='api_v1_appointment_detail'),
]
