import axios, { AxiosError } from 'axios';
import { JobResponse, JobCreate } from '../types/job';

// CQ-001: Externalized API base URL using Vite environment variables.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const getAuthHeaders = (apiKey: string) => ({
  'X-API-Key': apiKey,
});

export const getJobs = async (apiKey: string, skip: number = 0, limit: number = 100): Promise<JobResponse[]> => {
  const response = await apiClient.get<JobResponse[]>('/jobs', {
    headers: getAuthHeaders(apiKey),
    params: { skip, limit },
  });
  return response.data;
};

export const getJobDetails = async (jobId: string, apiKey: string): Promise<JobResponse> => {
  const response = await apiClient.get<JobResponse>(`/jobs/${jobId}`, {
    headers: getAuthHeaders(apiKey),
  });
  return response.data;
};

export const uploadFile = async (file: File, apiKey: string): Promise<{ message: string; object_path: string }> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<{ message: string; object_path: string }>('/upload-geospatial-data', formData, {
    headers: {
      ...getAuthHeaders(apiKey),
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const submitJob = async (jobData: JobCreate, apiKey: string): Promise<JobResponse> => {
  const response = await apiClient.post<JobResponse>('/solve', jobData, {
    headers: getAuthHeaders(apiKey),
  });
  return response.data;
};

export const downloadResult = async (jobId: string, fileType: 'geojson' | 'pdf', apiKey: string): Promise<Blob> => {
  const response = await apiClient.get(`/results/${jobId}/${fileType}`, {
    headers: getAuthHeaders(apiKey),
    responseType: 'blob', // Important for downloading files
  });
  return response.data;
};
