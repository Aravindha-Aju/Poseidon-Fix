import axios from 'axios';
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export const api = {
  runPipeline: async (caseId = "demo_case_001", imageId = "sample_sar_001", hoursBackward = 12) => {
    const response = await axios.post(`${API_BASE_URL}/pipeline/run`, { case_id: caseId, image_id: imageId, hours_backward: hoursBackward });
    return response.data;
  },
  // Keep legacy endpoints for backward compatibility
  detectSpill: async (imageId) => (await axios.post(`${API_BASE_URL}/detection/`, { image_id: imageId })).data,
  simulateDrift: async (centroid, timestamp, hours = 12) => (await axios.post(`${API_BASE_URL}/drift/`, { centroid, timestamp, hours_backward: hours })).data,
  getVessels: async (bbox, startTime, endTime) => (await axios.post(`${API_BASE_URL}/vessels/`, { bbox, start_time: startTime, end_time: endTime })).data.vessels
};

