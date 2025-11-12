import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { submitJob, uploadFile } from '../api/jobs';
import { JobCreate, SolverTypeEnum } from '../types/job';
import { useApiKey } from '../context/ApiKeyContext';
import { AxiosError } from 'axios';

const JobSubmission: React.FC = () => {
  const navigate = useNavigate();
  const { apiKey } = useApiKey();
  const [solverType, setSolverType] = useState<SolverTypeEnum>(SolverTypeEnum.CLASSICAL);
  const [parameters, setParameters] = useState<string>('{"grid_resolution": 50}');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState<boolean>(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!apiKey) {
      setMessage('Please set your API Key in the navigation bar.');
      setIsError(true);
      return;
    }

    setLoading(true);
    setMessage(null);
    setIsError(false);

    let inputDataPath: string | undefined = undefined;

    try {
      let parsedParameters: Record<string, any> = {};
      try {
        parsedParameters = JSON.parse(parameters);
      } catch (jsonError) {
        // CQ-002: Refined error handling for JSON parsing.
        throw new Error('Invalid JSON for parameters. Please ensure it is valid JSON.');
      }

      if (selectedFile) {
        setMessage('Uploading geospatial data...');
        const uploadResponse = await uploadFile(selectedFile, apiKey);
        inputDataPath = uploadResponse.object_path;
        setMessage(`File uploaded: ${inputDataPath}`);
      }

      setMessage('Submitting job...');
      const jobCreate: JobCreate = {
        solver_type: solverType,
        parameters: parsedParameters,
        input_data_path: inputDataPath,
      };

      const jobResponse = await submitJob(jobCreate, apiKey);
      setMessage(`Job submitted successfully! Job ID: ${jobResponse.id}`);
      setIsError(false);
      navigate(`/jobs/${jobResponse.id}`);
    } catch (error) {
      // CQ-002: Refined error handling for Axios errors and general errors.
      let errorMessage = 'An unexpected error occurred.';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      if (error instanceof AxiosError) {
        errorMessage = error.response?.data?.detail || error.message;
      }
      console.error('Job submission failed:', error);
      setMessage(`Error: ${errorMessage}`);
      setIsError(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Submit New Flood Simulation Job</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="solverType" className="label">Solver Type</label>
          <select
            id="solverType"
            value={solverType}
            onChange={(e) => setSolverType(e.target.value as SolverTypeEnum)}
            className="input-field"
            required
          >
            {Object.values(SolverTypeEnum).map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="parameters" className="label">Parameters (JSON)</label>
          <textarea
            id="parameters"
            value={parameters}
            onChange={(e) => setParameters(e.target.value)}
            rows={6}
            className="input-field font-mono"
            placeholder="e.g., {\"grid_resolution\": 50, \"conversion_factor\": 0.2}"
          />
          <p className="text-xs text-gray-500 mt-1">Provide job-specific parameters in JSON format.</p>
        </div>

        <div>
          <label htmlFor="geospatialFile" className="label">Geospatial Data File (Optional)</label>
          <input
            type="file"
            id="geospatialFile"
            onChange={handleFileChange}
            className="input-field file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <p className="text-xs text-gray-500 mt-1">Upload a geospatial data file (e.g., GeoTIFF, NetCDF, SHP, CSV) or a config file (e.g., JSON/text with grid_resolution).</p>
        </div>

        <button type="submit" className="btn-primary w-full" disabled={loading}>
          {loading ? 'Processing...' : 'Submit Job'}
        </button>
      </form>

      {message && (
        <div className={`mt-4 p-3 rounded-md ${isError ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default JobSubmission;
