"""
RK Hospital Bawaskar - Dental Informed Consent Templates
Pre-configured legal and clinical risk disclosures for major dental procedures.
"""

CONSENT_TEMPLATES = {
    'IMPLANT': {
        'title': 'Informed Consent for Surgical Placement of Dental Implants & Bone Grafting',
        'body': """1. NATURE OF PROCEDURE: I authorize Dr. Bawaskar / assigned surgeon to surgically place dental implant(s) into the alveolar bone of my jaw, and perform necessary bone augmentation/sinus elevation if required.

2. ANTICIPATED BENEFITS: Replacement of missing dentition with osseointegrated titanium fixtures to restore masticatory efficiency, aesthetics, and oral stability.

3. FORESEEABLE CLINICAL RISKS & COMPLICATIONS:
   • Nerve Paresthesia: Risk of temporary or rarely permanent altered sensation, tingling, or numbness of the lower lip, chin, tongue, teeth, or gums due to proximity to the inferior alveolar/mental/lingual nerves.
   • Sinus Involvement: For upper jaw implants, risk of sinus membrane perforation, acute sinusitis, or displacement.
   • Failure of Osseointegration: While success rates exceed 95%, implant failure to integrate with bone can occur due to host factors, infection, or micromotion, necessitating implant removal and delayed re-entry.
   • Infection, hematoma, swelling, post-operative bleeding, and trismus (limited jaw opening).
   • Need for bone graft or resorbable barrier membrane.

4. PATIENT COMMITMENT & RESPONSIBILITIES:
   • I confirm I have disclosed all medical conditions (Diabetes, Osteoporosis medications/Bisphosphonates, Blood thinners, Cardiac conditions).
   • I acknowledge that tobacco/smoking drastically increases implant failure rates by up to 40% and agree to minimize/cease smoking.
   • I commit to meticulous oral hygiene and attending scheduled recall maintenance every 6 months.

5. VOLUNTARY CONSENT: All alternatives (removable dentures, fixed bridges) have been explained. I consent freely to the procedure."""
    },

    'RCT': {
        'title': 'Informed Consent for Root Canal Treatment (Endodontic Therapy)',
        'body': """1. NATURE OF PROCEDURE: Root canal treatment involves the biomechanical cleaning, shaping, chemical disinfection, and three-dimensional hermetic filling (obturation) of diseased or necrotic dental pulp tissues to preserve the natural tooth.

2. CLINICAL RISKS & LIMITATIONS:
   • Instrument Separation: Due to microscopic canal curvature and calcification, fine nickel-titanium instruments may separate within the root canal. If this occurs, the fragment may be sealed within the root or require specialized surgical retrieval.
   • Root Perforation or Missed Canals: Complex root anatomy, accessory canals, or calcified pulp stones may present technical challenges or root perforations requiring specialized repair.
   • Post-Treatment Flare-up: Mild to moderate pain or swelling may occur for 24-72 hours following treatment and is managed with prescribed analgesics and antibiotics.
   • Persistent Infection: In chronic periapical lesions, apical surgery (apicoectomy) or extraction may be required if healing does not occur.

3. MANDATORY RESTORATIVE REQUIREMENT (CROWN):
   • I understand that an endodontically treated tooth becomes brittle over time. A permanent full-coverage crown (Zirconia / Ceramic / PFM) is ESSENTIAL within 3-4 weeks to prevent catastrophic tooth fracture. Failure to crown the tooth voids warranty against fracture.

4. VOLUNTARY CONSENT: The risks, costs, and alternatives (tooth extraction) have been discussed. I consent to root canal therapy."""
    },

    'EXTRACTION': {
        'title': 'Informed Consent for Surgical Tooth Extraction & Wisdom Disimpaction',
        'body': """1. NATURE OF PROCEDURE: Surgical or non-surgical removal of indicated tooth/teeth, including flap elevation, bone removal, and tooth sectioning if impacted.

2. FORESEEABLE RISKS & COMPLICATIONS:
   • Dry Socket (Alveolar Osteitis): Loss of blood clot resulting in throbbing pain after 48-72 hours, managed with sedative dressing.
   • Nerve Proximity: Temporary or, in rare cases, permanent numbness or tingling of the lip, chin, or tongue due to proximity of roots to the inferior alveolar nerve.
   • Maxillary Sinus Communication: For upper molars, root tips near the maxillary sinus may cause an oro-antral communication requiring surgical closure and nasal precautions.
   • Post-operative swelling, bruising, bleeding, trismus (jaw stiffness), and localized discomfort for 3-7 days.
   • Possible fracture of root tips requiring removal or retention based on surgical judgment.

3. POST-OPERATIVE PATIENT INSTRUCTIONS:
   • Maintain firm pressure on sterile gauze for 45-60 minutes.
   • DO NOT spit, rinse forcefully, suck through a straw, or smoke for 24 hours.
   • Apply ice pack externally on the cheek for the first 24 hours.
   • Take all prescribed analgesics and antibiotics as directed.

4. VOLUNTARY CONSENT: I have had all questions answered and consent to the extraction."""
    },

    'ANESTHESIA': {
        'title': 'Informed Consent for Local Anesthesia Administration',
        'body': """1. NATURE OF PROCEDURE: Administration of local anesthetic agents (Lignocaine, Articaine, Bupivacaine) with or without vasoconstrictor (Adrenaline 1:80,000 / 1:200,000) via infiltration or regional nerve block to ensure painless treatment.

2. RISKS & REVENUE:
   • Temporary numbness of lips, cheeks, and tongue lasting 2 to 5 hours.
   • Accidental biting/injury to numb lips or tongue, especially in pediatric patients.
   • Localized hematoma, tenderness at injection site, or temporary jaw stiffness (trismus).
   • Rare systemic reactions: Transient palpitations, lightheadedness, or allergic reactions.

3. MEDICAL DECLARATION: I have reported any history of cardiac disease, uncontrolled hypertension, asthma, thyroid disorder, or past adverse reactions to local anesthetics."""
    },

    'ORTHODONTIC': {
        'title': 'Informed Consent for Comprehensive Orthodontic Treatment & Clear Aligners',
        'body': """1. TREATMENT OBJECTIVES: Correction of malocclusion, teeth crowding/spacing, and jaw alignment using fixed brackets or removable clear aligners.

2. PATIENT RESPONSIBILITIES & RISKS:
   • Compliance: Aligners must be worn 20-22 hours daily. Poor compliance significantly prolongs treatment duration and compromises clinical outcomes.
   • Decalcification / White Spots: Inadequate oral hygiene during treatment will cause permanent enamel scarring and caries around brackets.
   • Mild Root Resorption: Slight shortening of root apices is a known biological phenomenon during tooth movement.
   • Retention: Lifelong retention (bonded wires and clear retainers) is mandatory. Failure to wear retainers leads to relapse.

3. CONSENT: I agree to follow all clinical protocols and keep scheduled adjustment appointments."""
    },

    'CROWN_BRIDGE': {
        'title': 'Informed Consent for Fixed Prosthodontic Crowns, Bridges & Veneers',
        'body': """1. PROCEDURE: Reduction and preparation of tooth structure followed by precision impression/digital scan, temporary restoration, and permanent cementation of CAD/CAM Zirconia, PFM, or E-Max ceramic restorations.

2. CLINICAL CONSIDERATIONS:
   • Transient temperature sensitivity for 1-2 weeks post-cementation.
   • Risk of pulpal irritation in heavily restored teeth which may necessitate root canal treatment.
   • Shade verification: I agree to approve the shade and aesthetics before permanent cementation.

3. CONSENT: I authorize the preparation and delivery of fixed prosthodontic restorations."""
    },

    'GENERAL': {
        'title': 'General Dental Treatment Informed Consent',
        'body': """1. I hereby authorize the clinical team at RK Hospital Bawaskar to perform necessary clinical examinations, diagnostic radiographs, intraoral photographs, and recommended restorative/periodontal procedures.
2. I understand that treatment plans may require modification as clinical conditions dictate during active therapy.
3. I agree to comply with post-operative recommendations and financial policies of the hospital."""
    }
}
