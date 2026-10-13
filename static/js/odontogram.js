/**
 * RK Hospital Bawaskar - Interactive Odontogram Engine
 * Supports 32 Adult + 20 Deciduous Teeth, 5-surface breakdown, Periodontal Charting
 */

document.addEventListener('DOMContentLoaded', function () {
  const toothUnits = document.querySelectorAll('.tooth-unit');
  const modal = document.getElementById('toothModal');
  if (!modal) return;

  const patientId = modal.dataset.patientId;
  const modalTitle = document.getElementById('modalToothTitle');
  const statusSelect = document.getElementById('modalToothStatus');
  const surfM = document.getElementById('surfMesial');
  const surfD = document.getElementById('surfDistal');
  const surfO = document.getElementById('surfOcclusal');
  const surfB = document.getElementById('surfBuccal');
  const surfL = document.getElementById('surfLingual');
  const pocketInput = document.getElementById('modalPocketDepth');
  const mobilitySelect = document.getElementById('modalMobility');
  const bopCheck = document.getElementById('modalBop');
  const notesText = document.getElementById('modalNotes');
  const procSelect = document.getElementById('modalProcedureSelect');
  const saveBtn = document.getElementById('modalSaveToothBtn');
  const closeBtn = document.getElementById('modalCloseBtn');

  let currentToothNumber = null;

  function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.getAttribute('content');
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  // Tooth click listener
  toothUnits.forEach(tooth => {
    tooth.addEventListener('click', function () {
      const toothNum = this.dataset.toothNumber;
      currentToothNumber = toothNum;

      toothUnits.forEach(t => t.classList.remove('selected'));
      this.classList.add('selected');

      modalTitle.innerText = `Tooth #${toothNum} - Clinical Examination & Treatment`;

      // Fetch tooth data
      fetch(`/api/tooth/${patientId}/${toothNum}/`)
        .then(res => res.json())
        .then(data => {
          statusSelect.value = data.status || 'HEALTHY';
          surfM.checked = Boolean(data.mesial);
          surfD.checked = Boolean(data.distal);
          surfO.checked = Boolean(data.occlusal);
          surfB.checked = Boolean(data.buccal);
          surfL.checked = Boolean(data.lingual);
          pocketInput.value = data.pocket_depth_mm || 2;
          mobilitySelect.value = data.mobility || 0;
          bopCheck.checked = Boolean(data.bleeding_on_probing);
          notesText.value = data.clinical_notes || '';
          if (procSelect) procSelect.value = '';

          modal.classList.add('active');
        })
        .catch(err => {
          console.error('Error fetching tooth data:', err);
          modal.classList.add('active');
        });
    });
  });

  // Close modal
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.classList.remove('active');
  });

  // Save Tooth Data
  if (saveBtn) {
    saveBtn.addEventListener('click', function () {
      if (!currentToothNumber) return;

      const payload = {
        status: statusSelect.value,
        mesial: surfM.checked,
        distal: surfD.checked,
        occlusal: surfO.checked,
        buccal: surfB.checked,
        lingual: surfL.checked,
        pocket_depth_mm: parseInt(pocketInput.value, 10) || 2,
        mobility: parseInt(mobilitySelect.value, 10) || 0,
        bleeding_on_probing: bopCheck.checked,
        clinical_notes: notesText.value,
        procedure_id: procSelect ? procSelect.value : null
      };

      saveBtn.innerText = 'Saving...';
      saveBtn.disabled = true;

      fetch(`/api/tooth/${patientId}/${currentToothNumber}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(payload)
      })
        .then(res => res.json())
        .then(data => {
          saveBtn.innerText = 'Save Changes';
          saveBtn.disabled = false;

          if (data.success) {
            // Update the DOM tooth element visually
            const targetEl = document.querySelector(`.tooth-unit[data-tooth-number="${currentToothNumber}"]`);
            if (targetEl) {
              const visual = targetEl.querySelector('.tooth-visual');
              // Clear previous status classes
              visual.className = `tooth-visual tooth-status-${payload.status}`;

              // Update surfaces highlight
              const surfCells = visual.querySelectorAll('.surf-cell');
              if (surfCells.length >= 5) {
                // [0]=Buccal, [1]=Lingual, [2]=Mesial, [3]=Distal, [4]=Occlusal
                surfCells[0].classList.toggle('active-surface', payload.buccal);
                surfCells[1].classList.toggle('active-surface', payload.lingual);
                surfCells[2].classList.toggle('active-surface', payload.mesial);
                surfCells[3].classList.toggle('active-surface', payload.distal);
                surfCells[4].classList.toggle('active-surface', payload.occlusal);
              }
            }
            modal.classList.remove('active');
            // Show toast message
            showToast(`Tooth #${currentToothNumber} updated to ${data.status_display}`);
          } else {
            alert('Error updating tooth: ' + (data.error || 'Unknown error'));
          }
        })
        .catch(err => {
          saveBtn.innerText = 'Save Changes';
          saveBtn.disabled = false;
          console.error(err);
          alert('Network error while saving tooth.');
        });
    });
  }

  // Dentition Toggle (Adult vs Pediatric)
  const adultBtn = document.getElementById('viewAdultDentition');
  const pediaBtn = document.getElementById('viewPediatricDentition');
  const adultArch = document.getElementById('adultDentitionArch');
  const pediaArch = document.getElementById('pediatricDentitionArch');

  if (adultBtn && pediaBtn && adultArch && pediaArch) {
    adultBtn.addEventListener('click', () => {
      adultBtn.classList.add('btn-primary');
      adultBtn.classList.remove('btn-secondary');
      pediaBtn.classList.add('btn-secondary');
      pediaBtn.classList.remove('btn-primary');
      adultArch.style.display = 'block';
      pediaArch.style.display = 'none';
    });

    pediaBtn.addEventListener('click', () => {
      pediaBtn.classList.add('btn-primary');
      pediaBtn.classList.remove('btn-secondary');
      adultBtn.classList.add('btn-secondary');
      adultBtn.classList.remove('btn-primary');
      adultArch.style.display = 'none';
      pediaArch.style.display = 'block';
    });
  }
});

function showToast(msg) {
  let toast = document.getElementById('globalToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'globalToast';
    toast.style.position = 'fixed';
    toast.style.bottom = '24px';
    toast.style.right = '24px';
    toast.style.background = '#0f172a';
    toast.style.color = '#ffffff';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = '10px';
    toast.style.boxShadow = '0 10px 25px rgba(0,0,0,0.2)';
    toast.style.zIndex = '9999';
    toast.style.fontSize = '0.9rem';
    toast.style.fontWeight = '500';
    toast.style.transition = 'opacity 0.3s ease';
    document.body.appendChild(toast);
  }
  toast.innerText = msg;
  toast.style.opacity = '1';
  setTimeout(() => {
    toast.style.opacity = '0';
  }, 3500);
}
