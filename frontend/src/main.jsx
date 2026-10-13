import React from 'react';
import { createRoot } from 'react-dom/client';
import AdvancedOdontogramApp from './AdvancedOdontogramApp';
import './odontogram-styles.css';

// Active mounted roots registry
const mountedRoots = new Map();

/**
 * Mount the Advanced Dental Odontogram into a target DOM container.
 *
 * @param {HTMLElement|string} target - Container element or CSS selector
 * @param {Object} options - Configuration options
 */
export function mountAdvancedOdontogram(target, options = {}) {
  const container = typeof target === 'string' ? document.querySelector(target) : target;
  if (!container) {
    console.error('[RK Odontogram] Target container not found:', target);
    return null;
  }

  // Unmount existing root if present
  if (mountedRoots.has(container)) {
    try {
      mountedRoots.get(container).unmount();
      mountedRoots.delete(container);
    } catch (e) {
      console.warn('[RK Odontogram] Cleaned previous root:', e);
    }
  }

  // Read dataset attributes if available
  const patientId = options.patientId || container.dataset.patientId || null;
  const patientName = options.patientName || container.dataset.patientName || 'Patient';
  const patientMrn = options.patientMrn || container.dataset.patientMrn || '';
  const csrfToken = options.csrfToken || container.dataset.csrfToken || '';
  const saveUrl = options.saveUrl || container.dataset.saveUrl || '';
  const readOnly = options.readOnly !== undefined ? options.readOnly : container.dataset.readOnly === 'true';
  const userRole = options.userRole || container.dataset.userRole || 'DENTIST';

  let initialData = options.initialData || null;
  if (!initialData && container.dataset.initialData) {
    try {
      initialData = JSON.parse(container.dataset.initialData);
    } catch (err) {
      console.warn('[RK Odontogram] Failed to parse initialData dataset:', err);
    }
  }

  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <AdvancedOdontogramApp
        patientId={patientId}
        patientName={patientName}
        patientMrn={patientMrn}
        csrfToken={csrfToken}
        saveUrl={saveUrl}
        readOnly={readOnly}
        userRole={userRole}
        initialData={initialData}
        onSaveSuccess={options.onSaveSuccess}
      />
    </React.StrictMode>
  );

  mountedRoots.set(container, root);
  return root;
}

/**
 * Unmount an active odontogram root
 */
export function unmountAdvancedOdontogram(target) {
  const container = typeof target === 'string' ? document.querySelector(target) : target;
  if (container && mountedRoots.has(container)) {
    mountedRoots.get(container).unmount();
    mountedRoots.delete(container);
  }
}

// Attach to window object for global browser access in Django templates
if (typeof window !== 'undefined') {
  window.mountAdvancedOdontogram = mountAdvancedOdontogram;
  window.unmountAdvancedOdontogram = unmountAdvancedOdontogram;

  // Auto-mount if default root exists
  const autoInit = () => {
    const defaultRoot = document.getElementById('react-odontogram-root');
    if (defaultRoot && !mountedRoots.has(defaultRoot)) {
      mountAdvancedOdontogram(defaultRoot);
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }
}
