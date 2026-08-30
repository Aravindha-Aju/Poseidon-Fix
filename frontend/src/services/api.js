const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const runPipeline = async (caseId = 'demo_case_001', imageId = 'sample_001') => {
  const response = await fetch(`${API_BASE_URL}/pipeline/run`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, image_id: imageId }),
  });
  if (!response.ok) throw new Error(`Pipeline failed: ${response.statusText}`);
  return await response.json();
};

export const downloadEvidenceJSON = (evidenceData, filename = 'poseidon_evidence.json') => {
  const blob = new Blob([JSON.stringify(evidenceData, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href = url; a.download = filename;
  document.body.appendChild(a); a.click(); document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

