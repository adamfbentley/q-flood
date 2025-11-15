import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { getJobDetails, downloadResult } from '../api/jobs';
import { JobResponse, JobStatusEnum } from '../types/job';
import { useApiKey } from '../context/ApiKeyContext';
import { AxiosError } from 'axios';
import { toast } from 'react-toastify';
import FloodMap3D from '../components/FloodMap3D'; // Import the 3D map component
import SimpleFloodMap from '../components/SimpleFloodMap'; // Import the fallback component

const JobDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { apiKey } = useApiKey();
  const [job, setJob] = useState<JobResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [geojson_data, setGeojsonData] = useState<GeoJSON.FeatureCollection | null>(null); // New state for GeoJSON

  // CQ-008: Use useRef to hold the latest job state for the polling interval
  const jobRef = useRef(job);
  useEffect(() => {
    jobRef.current = job;
  }, [job]);

  const fetchJob = useCallback(async () => {
    if (!id) return;
    if (!apiKey) {
      setError('API Key is not set. Please set it in the navigation bar.');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const fetchedJob = await getJobDetails(id, apiKey);
      setJob(fetchedJob);

      // Fetch GeoJSON data if available and not already fetched
      if (fetchedJob.geojson_path && [JobStatusEnum.COMPLETED, JobStatusEnum.FALLBACK_CLASSICAL_COMPLETED].includes(fetchedJob.status) && !geojson_data) {
        try {
          const blob = await downloadResult(id, 'geojson', apiKey);
          const text = await blob.text();
          const parsedGeojson = JSON.parse(text) as GeoJSON.FeatureCollection;
          setGeojsonData(parsedGeojson);
        } catch (geojsonError) {
          console.error('Failed to load GeoJSON for visualization:', geojsonError);
          toast.error('Failed to load GeoJSON data for visualization.'); // CQ-S6-003: Added user-facing error notification
        }
      }
    } catch (err) {
      // CQ-004: Refined error handling for Axios errors and general errors.
      let errorMessage = 'An unexpected error occurred.';
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      if (err instanceof AxiosError) {
        errorMessage = err.response?.data?.detail || err.message;
      }
      console.error('Failed to fetch job details:', err);
      setError(`Failed to fetch job details: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }, [id, apiKey, geojson_data]); // Added geojson_data to dependencies to prevent re-fetching if already present

  useEffect(() => {
    fetchJob();

    // CQ-008: Refactored useEffect for polling.
    // The interval now checks jobRef.current.status to avoid re-running the effect when 'job' state updates.
    const interval = setInterval(() => {
      if (jobRef.current && ![JobStatusEnum.COMPLETED, JobStatusEnum.FAILED, JobStatusEnum.CANCELLED, JobStatusEnum.FALLBACK_CLASSICAL_COMPLETED, JobStatusEnum.FALLBACK_CLASSICAL_FAILED].includes(jobRef.current.status)) {
        fetchJob();
      } else if (jobRef.current && [JobStatusEnum.COMPLETED, JobStatusEnum.FAILED, JobStatusEnum.CANCELLED, JobStatusEnum.FALLBACK_CLASSICAL_COMPLETED, JobStatusEnum.FALLBACK_CLASSICAL_FAILED].includes(jobRef.current.status)) {
        // If job is completed/failed, clear the interval
        clearInterval(interval);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [id, apiKey, fetchJob]);

  const handleDownload = async (fileType: 'geojson' | 'pdf') => {
    if (!id || !apiKey) {
      toast.error('Missing Job ID or API Key for download.');
      return;
    }
    try {
      const blob = await downloadResult(id, fileType, apiKey);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${fileType}_${id}.${fileType}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      toast.success(`Successfully downloaded ${fileType} file.`);
    } catch (err) {
      // CQ-006: Replaced alert() with react-toastify for better UX.
      // CQ-004: Refined error handling for Axios errors and general errors.
      let errorMessage = 'An unexpected error occurred during download.';
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      if (err instanceof AxiosError) {
        errorMessage = err.response?.data?.detail || err.message;
      }
      console.error(`Failed to download ${fileType}:`, err);
      toast.error(`Failed to download ${fileType}: ${errorMessage}`);
    }
  };

  if (loading) {
    return <div className="text-center text-gray-600">Loading job details...</div>;
  }

  if (error) {
    return <div className="bg-red-100 text-red-800 p-3 rounded-md">{error}</div>;
  }

  if (!job) {
    return <div className="bg-yellow-100 text-yellow-800 p-3 rounded-md">Job not found.</div>;
  }

  const isJobCompleted = [JobStatusEnum.COMPLETED, JobStatusEnum.FALLBACK_CLASSICAL_COMPLETED].includes(job.status);

  return (
    <div className="p-6 bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Job Details: {job.id.substring(0, 8)}...</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-700">
        <div>
          <p><strong className="font-medium">Job ID:</strong> {job.id}</p>
          <p><strong className="font-medium">Status:</strong> {job.status}</p>
          <p><strong className="font-medium">Solver Type:</strong> {job.solver_type}</p>
          <p><strong className="font-medium">Created At:</strong> {new Date(job.created_at).toLocaleString()}</p>
          <p><strong className="font-medium">Updated At:</strong> {new Date(job.updated_at).toLocaleString()}</p>
          {job.fallback_reason && <p><strong className="font-medium text-red-600">Fallback Reason:</strong> {job.fallback_reason}</p>}
        </div>
        <div>
          <p><strong className="font-medium">Input Data Path:</strong> {job.input_data_path || 'N/A'}</p>
          <p><strong className="font-medium">Matrix Path:</strong> {job.matrix_path || 'N/A'}</p>
          <p><strong className="font-medium">Vector Path:</strong> {job.vector_path || 'N/A'}</p>
          <p><strong className="font-medium">Solution Path:</strong> {job.solution_path || 'N/A'}</p>
          <p><strong className="font-medium">GeoJSON Path:</strong> {job.geojson_path || 'N/A'}</p>
          <p><strong className="font-medium">PDF Report Path:</strong> {job.pdf_report_path || 'N/A'}</p>
        </div>
      </div>

      <div className="mt-6">
        <h3 className="text-xl font-semibold mb-2 text-gray-800">Parameters:</h3>
        <pre className="bg-gray-50 p-4 rounded-md text-sm overflow-x-auto">
          {JSON.stringify(job.parameters, null, 2)}
        </pre>
      </div>

      {isJobCompleted && geojson_data && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">Flood Map Visualization:</h3>
          {import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ? (
            <FloodMap3D geojson={geojson_data} />
          ) : (
            <SimpleFloodMap geojson={geojson_data} />
          )}
        </div>
      )}

      {isJobCompleted && (job.geojson_path || job.pdf_report_path) && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">Results:</h3>
          <div className="flex space-x-4">
            {job.geojson_path && (
              <button onClick={() => handleDownload('geojson')} className="btn-primary">
                Download GeoJSON
              </button>
            )}
            {job.pdf_report_path && (
              <button onClick={() => handleDownload('pdf')} className="btn-primary">
                Download PDF Report
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetail;
