# RK Hospital Bawaskar - Dental Hospital Management System & Visual Dental EMR

A specialized Django-based Hospital Management System with an Interactive Dental EMR, designed specifically for dental surgical workflows, multi-operatory chair management, dental lab fabrication tracking, digital dental prescriptions, and role-based access control.

---

## 🌟 Key Modules & Capabilities

### 1. 🦷 Interactive Visual Odontogram (Dental Charting Engine)
- **Adult (32 Teeth)** & **Pediatric (20 Deciduous Teeth)** FDI notation visual charts.
- **5-Surface Anatomy**: Independent surface-level diagnosis & restoration tracking for **Mesial (M)**, **Distal (D)**, **Occlusal/Incisal (O/I)**, **Buccal/Facial (B)**, and **Lingual/Palatal (L)**.
- **Clinical Condition Coding**: Color-coded states for Healthy, Dental Caries (Decay), Composite/Amalgam Filled, Root Canal Treated (RCT), Crowns/Caps, Implants, Missing/Extracted, and Impacted Wisdom teeth.
- **Periodontal Charting**: Probing pocket depth (mm), mobility grade (0, I, II, III), bleeding on probing (BOP).
- **Real-Time AJAX Synchronization**: Updates persist without full-page reloads.

### 2. 💺 Operatory Chairs & Real-Time Queue
- Multi-chair visual scheduling (Operatory A: Conservative & Micro-Endo, Operatory B: Surgical & Implants, Operatory C: Ortho, Operatory D: Hygiene & Preventive).
- Status pipeline: `Scheduled` ➔ `Checked In (Lounge)` ➔ `In Chair` ➔ `Completed`.

### 3. 🔬 Dental Lab Work Tracking
- Tracks prosthodontic & orthodontic lab cases (Zirconia Crowns, PFM, Aligners, Dentures, Nightguards).
- Records Vita shade guide, margin specs, sent date, expected delivery, and status (`Impression Sent` ➔ `In Fabrication` ➔ `Received at Clinic` ➔ `Fitted`).

### 4. 💊 Digital Dental Prescriptions (Rx)
- Pre-configured dental medicine presets (Augmentin 625mg, Zerodol-SP, Metrogyl, Ketorol-DT, Hexidine Mouthwash).
- Formal doctor prescription pad with doctor registration number, advice, and printable format.

### 5. 💰 Dental Billing & Printable Tax Invoices
- Procedure catalog with pre-seeded prices.
- Itemized invoicing with discounts, tax calculations, and partial payments tracking.
- Multiple payment modes (UPI / GPay / QR, Cash, Card, Insurance).
- Official Hospital Tax Invoice & Receipt layout with authorized signature block.

### 6. 📦 Dental Material Inventory & Store
- Manages local anesthetics, composite syringes, rotary files, impression materials, and surgical sutures.
- Low-stock alerts and rapid one-click restocking.

---

## 👥 Role-Based Logins & Credentials

The system is configured with a **fresh database (0 patients)** and the following pre-configured staff accounts:

| Role | Username | Password | Full Name & Title | Specialty Focus |
|---|---|---|---|---|
| **Hospital Director & Super Administrator** | `admin` | `Anurag@268724` | Admin (Dr. Anurag Bawaskar) | Medical Director • Full Master Access |
| **Senior Dentist (Endodontist)** | `dr.sharma` | `dentist123` | Dr. Priya Sharma | Conservative Dentistry & Visual EMR |
| **Orthodontist (Dentist)** | `dr.kapoor` | `dentist123` | Dr. Rohan Kapoor | Orthodontics & Clear Aligners |
| **Front Desk (Reception)** | `reception` | `reception123` | Sneha Verma | OPD Coordination & Registration |
| **Dental Hygienist (Nurse)** | `hygienist` | `hygienist123` | Pooja Shinde | Prophylaxis & Sterilization |
| **Pharmacy / Store Manager** | `pharmacy` | `pharmacy123` | Amit Deshmukh | Material Store & Dispensary |

> ⚡ **Clean Fresh State:** All mock patients have been cleared. Log in as **`admin`** to start adding real patients and clinical records.
> ⚡ **Quick Login:** The login screen (`/login/`) includes an **Auto-Fill Admin** button to enter credentials with one tap.

---

## 🚀 Running the Project

```bash
# Navigate to project directory
cd /Users/anurag.bawaskar/.gemini/antigravity-ide/scratch/rk_hospital_bawaskar

# Activate virtual environment
source venv/bin/activate

# Start the development server
python manage.py runserver 0.0.0.0:8000
```

Open your browser at: **[http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)**

---

## 🌐 Deploying to GitHub Pages (`*.github.io`)

This repository is pre-configured with a standalone, mobile-responsive interactive showcase in the `docs/` folder, plus an automated GitHub Actions deployment workflow.

### 3-Step Setup to Launch on `github.io`:

1. **Push this repository to your GitHub account**:
   ```bash
   # Add all files and commit
   git add -A
   git commit -m "Launch RK Hospital Bawaskar on GitHub Pages"

   # Point to your GitHub repository (create an empty repo on github.com first)
   git branch -M main
   git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git
   git push -u origin main
   ```

2. **Enable GitHub Pages in your Repository Settings**:
   - Navigate to your repository on GitHub (`https://github.com/<username>/<repo>`).
   - Click **Settings** (gear icon at the top).
   - In the left sidebar, click **Pages**.
   - Under **Build and deployment > Source**:
     - Choose **Deploy from a branch**.
     - Branch: Select **`main`** and folder: **`/docs`**.
     - Click **Save**.
     *(Alternatively, you can choose "GitHub Actions" to use the pre-built workflow in `.github/workflows/deploy-pages.yml`)*

3. **Visit Your Live Application**:
   Within 1-2 minutes, GitHub will publish your live application at:
   ```
   https://<YOUR_GITHUB_USERNAME>.github.io/<YOUR_REPOSITORY_NAME>/
   ```

---

## 🚀 Deploying Full-Stack Django on Render.com

This repository is **100% Render-ready** with a pre-configured `render.yaml` Blueprint, Gunicorn WSGI server, WhiteNoise static compression, and automatic database migration & seeding.

### Option A: 1-Click Blueprint Deploy (Fastest)

1. Push this repository to your GitHub account:
   ```bash
   git add -A
   git commit -m "Configure Render production deployment"
   git push -u origin main
   ```
2. Log in to [Render.com](https://dashboard.render.com).
3. Click **New +** > **Blueprint**.
4. Connect your GitHub repository (`rk-hospital-bawaskar`).
5. Render will automatically read [`render.yaml`](file:///Users/anurag.bawaskar/.gemini/antigravity-ide/scratch/rk_hospital_bawaskar/render.yaml) and configure the web service, build script, environment variables, and start command.
6. Click **Apply**. Within ~2 minutes, your live dental hospital app will be live on Render!

---

### Option B: Manual Web Service Setup on Render

If you prefer to configure manually on Render without Blueprints:

1. In the Render Dashboard, click **New +** > **Web Service**.
2. Select **Build and deploy from a Git repository** and pick your repo.
3. Configure the following fields:
   * **Name**: `rk-hospital-bawaskar`
   * **Region**: Any (e.g., Singapore, Frankfurt, or Oregon)
   * **Branch**: `main`
   * **Language**: `Python`
   * **Build Command**: `./build.sh`
   * **Start Command**: `gunicorn rk_hospital_core.wsgi:application`
   * **Instance Type**: `Free`
4. Under **Environment Variables**, add:
   * `PYTHON_VERSION`: `3.12.4`
   * `SECRET_KEY`: *(Click "Generate" or enter a secure string)*
   * `DEBUG`: `False`
   * `RENDER`: `true`
5. Click **Create Web Service**.

Render will automatically run `./build.sh`, install all requirements, collect static files, run database migrations, seed all 6 role accounts (`dr.bawaskar`, `dr.sharma`, etc.), and launch Gunicorn!

Your hospital application will be live at:
`https://rk-hospital-bawaskar.onrender.com`


