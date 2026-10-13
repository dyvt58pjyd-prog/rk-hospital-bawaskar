import React, { useState, useEffect, useRef } from 'react';
import {
  OdontogramShell,
  getStatusChart,
  importStatus,
  exportFhir,
  exportImage,
  exportSvg,
  exportPdf,
  onStateChange,
  applyPrimaryDentition,
  applyMixedDentition,
} from 'react-advanced-odontogram';
import 'react-advanced-odontogram/style.css';

export default function AdvancedOdontogramApp({
  patientId,
  patientName = 'Patient',
  patientMrn = '',
  initialData = null,
  csrfToken = '',
  saveUrl = '',
  readOnly = false,
  userRole = 'DENTIST',
  onSaveSuccess = null,
}) {
  const [saveStatus, setSaveStatus] = useState('saved'); // 'saved', 'dirty', 'saving', 'error'
  const [statusMessage, setStatusMessage] = useState('Ready');
  const [numberingSystem, setNumberingSystem] = useState('FDI');
  const [darkMode, setDarkMode] = useState(false);
  const [dentitionType, setDentitionType] = useState('adult');
  const hasLoadedRef = useRef(false);

  // Initialize data on mount
  useEffect(() => {
    if (hasLoadedRef.current) return;

    const loadData = async () => {
      try {
        let chartData = initialData;
        if (!chartData && patientId) {
          // Fetch from Django API
          const res = await fetch(`/api/odontogram/${patientId}/state/`);
          if (res.ok) {
            const data = await res.json();
            if (data && data.chart_data && Object.keys(data.chart_data).length > 0) {
              chartData = data.chart_data;
            }
          }
        }

        if (chartData && typeof chartData === 'object' && Object.keys(chartData).length > 0) {
          setTimeout(() => {
            try {
              importStatus(chartData);
              setStatusMessage('Chart synchronized with EMR');
            } catch (err) {
              console.warn('Initial importStatus warning:', err);
            }
          }, 200);
        }
        hasLoadedRef.current = true;
      } catch (err) {
        console.error('Error fetching initial odontogram state:', err);
      }
    };

    loadData();

    // Subscribe to state changes to flag dirty
    const unsubscribe = onStateChange(() => {
      if (hasLoadedRef.current) {
        setSaveStatus('dirty');
        setStatusMessage('Unsaved changes in chart');
      }
    });

    return () => {
      if (typeof unsubscribe === 'function') unsubscribe();
    };
  }, [patientId, initialData]);

  // Save current status to Django backend
  const handleSaveToEmr = async () => {
    if (readOnly) return;
    try {
      setSaveStatus('saving');
      setStatusMessage('Saving chart to EMR database...');

      const currentChart = getStatusChart();
      const targetUrl = saveUrl || `/api/odontogram/${patientId}/state/`;

      const response = await fetch(targetUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
          patient_id: patientId,
          chart_data: currentChart,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const resJson = await response.json();
      setSaveStatus('saved');
      setStatusMessage(`Saved successfully (${new Date().toLocaleTimeString()})`);

      if (onSaveSuccess && typeof onSaveSuccess === 'function') {
        onSaveSuccess(resJson);
      }
    } catch (err) {
      console.error('Save to EMR failed:', err);
      setSaveStatus('error');
      setStatusMessage('Error saving: ' + (err.message || 'Check network'));
    }
  };

  // Export HL7 FHIR Bundle
  const handleExportFhir = () => {
    try {
      const bundle = exportFhir({
        subject: `Patient/${patientId || '1'}`,
      });
      const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(bundle, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute('href', dataStr);
      downloadAnchor.setAttribute('download', `FHIR_R4_Odontogram_${patientMrn || patientId || 'chart'}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
      setStatusMessage('Exported FHIR R4 bundle');
    } catch (err) {
      console.error('FHIR export error:', err);
      alert('Could not export FHIR: ' + err.message);
    }
  };

  // Export High-Res Image
  const handleExportImage = async (format = 'png') => {
    try {
      setStatusMessage(`Exporting ${format.toUpperCase()} chart...`);
      await exportImage(format);
      setStatusMessage(`Chart exported as ${format.toUpperCase()}`);
    } catch (err) {
      console.error('Image export error:', err);
    }
  };

  // Export SVG
  const handleExportSvg = async () => {
    try {
      setStatusMessage('Exporting Vector SVG...');
      await exportSvg();
      setStatusMessage('SVG chart exported');
    } catch (err) {
      console.error('SVG export error:', err);
    }
  };

  // Switch dentition preset
  const handleDentitionChange = (type) => {
    setDentitionType(type);
    if (type === 'pediatric') {
      try {
        applyPrimaryDentition();
        setStatusMessage('Deciduous dentition applied');
      } catch (e) {
        console.warn(e);
      }
    } else if (type === 'mixed') {
      try {
        applyMixedDentition();
        setStatusMessage('Mixed dentition applied');
      } catch (e) {
        console.warn(e);
      }
    } else {
      setStatusMessage('Adult dentition active');
    }
  };

  return (
    <div className={`rk-odontogram-container ${darkMode ? 'dark' : ''}`}>
      {/* Premium Hospital Studio Action Bar */}
      <div className="rk-studio-bar">
        <div className="rk-studio-left">
          <div className="rk-hospital-badge">
            <span className="rk-badge-dot"></span>
            <strong>RK HOSPITAL BAWASKAR</strong>
            <span className="rk-badge-sep">•</span>
            <span>DENTAL EMR STUDIO</span>
          </div>

          <div className="rk-patient-chip">
            <span className="rk-chip-icon">👤</span>
            <span className="rk-patient-name">{patientName}</span>
            {patientMrn && <span className="rk-patient-mrn">({patientMrn})</span>}
          </div>

          {readOnly && (
            <span className="rk-readonly-pill">Read Only (Portal Mode)</span>
          )}
        </div>

        <div className="rk-studio-center">
          <div className={`rk-status-indicator rk-status-${saveStatus}`}>
            <span className="rk-status-dot"></span>
            <span className="rk-status-text">{statusMessage}</span>
          </div>
        </div>

        <div className="rk-studio-right">
          {/* Dentition Selector */}
          <div className="rk-btn-group">
            <button
              type="button"
              className={`rk-btn rk-btn-xs ${dentitionType === 'adult' ? 'active' : ''}`}
              onClick={() => handleDentitionChange('adult')}
              title="Standard 32 permanent teeth"
            >
              Permanent (32)
            </button>
            <button
              type="button"
              className={`rk-btn rk-btn-xs ${dentitionType === 'mixed' ? 'active' : ''}`}
              onClick={() => handleDentitionChange('mixed')}
              title="Mixed dentition"
            >
              Mixed
            </button>
            <button
              type="button"
              className={`rk-btn rk-btn-xs ${dentitionType === 'pediatric' ? 'active' : ''}`}
              onClick={() => handleDentitionChange('pediatric')}
              title="20 deciduous primary teeth"
            >
              Pediatric (20)
            </button>
          </div>

          {/* Numbering Selector */}
          <select
            className="rk-select-compact"
            value={numberingSystem}
            onChange={(e) => setNumberingSystem(e.target.value)}
            title="Dental Numbering System"
          >
            <option value="FDI">FDI (11-48 / 51-85)</option>
            <option value="Universal">Universal (1-32 / A-T)</option>
            <option value="Palmer">Palmer Notation</option>
          </select>

          {/* Export Dropdown / Actions */}
          <div className="rk-export-group">
            <button
              type="button"
              className="rk-btn rk-btn-outline rk-btn-sm"
              onClick={handleExportFhir}
              title="Export HL7 FHIR R4 Diagnostic Observation Bundle"
            >
              FHIR R4
            </button>
            <button
              type="button"
              className="rk-btn rk-btn-outline rk-btn-sm"
              onClick={() => handleExportImage('png')}
              title="Download high-resolution PNG chart"
            >
              PNG
            </button>
            <button
              type="button"
              className="rk-btn rk-btn-outline rk-btn-sm"
              onClick={handleExportSvg}
              title="Download vector SVG"
            >
              SVG
            </button>
          </div>

          {/* Save to EMR button */}
          {!readOnly && (
            <button
              type="button"
              className={`rk-btn rk-btn-save rk-btn-sm ${saveStatus === 'dirty' ? 'rk-btn-pulse' : ''}`}
              onClick={handleSaveToEmr}
              disabled={saveStatus === 'saving'}
            >
              {saveStatus === 'saving' ? (
                <>
                  <span className="rk-spinner"></span>
                  Saving...
                </>
              ) : (
                <>
                  <span>💾</span> Save EMR Chart
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Main Odontogram Shell Container */}
      <div className="rk-odontogram-shell-wrapper">
        <OdontogramShell
          numberingSystem={numberingSystem}
          onNumberingChange={setNumberingSystem}
          darkMode={darkMode}
          onDarkModeChange={setDarkMode}
          readOnly={readOnly}
          enableNotes={true}
          enableIcdas={true}
          cariesDepthEnabled={true}
          pulpDetailLevel="aae"
          secondaryCariesMode="standard"
          rootCariesMode="severity"
        />
      </div>
    </div>
  );
}
