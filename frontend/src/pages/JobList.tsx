import React, { useEffect, useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { getJobs } from '../api/jobs';
import { JobResponse } from '../types/job';
import { useApiKey } from '../context/ApiKeyContext';
import { AxiosError } from 'axios';

const JobList: React.FC = () => {
  const { apiKey } = useApiKey();
  const [jobs, setJobs] = useState<JobResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState<number>(0);
  const [limit, setLimit] = useState<number>(10);
  const [hasMore, setHasMore] = useState<boolean>(true);

  const fetchJobs = useCallback(async (currentSkip: number, currentLimit: number) => {
    if (!apiKey) {
      setError('API Key is not set. Please set it in the navigation bar.');
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const fetchedJobs = await getJobs(apiKey, currentSkip, currentLimit);
      setJobs((prevJobs) => {
        const newJobs = [...prevJobs, ...fetchedJobs];
        // CQ-007: Optimized duplicate filtering using a Map for better performance.
        const uniqueJobsMap = new Map<string, JobResponse>();
        newJobs.forEach(job => uniqueJobsMap.set(job.id, job));
        const uniqueJobs = Array.from(uniqueJobsMap.values());
        
        // Sort by created_at in descending order
        return uniqueJobs.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
      });
      setHasMore(fetchedJobs.length === currentLimit);
    } catch (err) {
      // CQ-003: Refined error handling for Axios errors and general errors.
      let errorMessage = 'An unexpected error occurred.';
      if (err instanceof Error) {
        errorMessage = err.message;
      }
      if (err instanceof AxiosError) {
        errorMessage = err.response?.data?.detail || err.message;
      }
      console.error('Failed to fetch jobs:', err);
      setError(`Failed to fetch jobs: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  }, [apiKey, limit]);

  useEffect(() => {
    setJobs([]); // Clear jobs when API key changes or component mounts
    setSkip(0);
    setHasMore(true);
    if (apiKey) {
      fetchJobs(0, limit);
    }
  }, [apiKey, limit, fetchJobs]);

  const handleLoadMore = () => {
    setSkip((prevSkip) => {
      const nextSkip = prevSkip + limit;
      fetchJobs(nextSkip, limit);
      return nextSkip;
    });
  };

  return (
    <div className="p-6 bg-white shadow-md rounded-lg">
      <h2 className="text-2xl font-semibold mb-6 text-gray-800">Flood Simulation Jobs</h2>

      {error && <div className="bg-red-100 text-red-800 p-3 rounded-md mb-4">{error}</div>}

      {loading && jobs.length === 0 && <p className="text-gray-600">Loading jobs...</p>}

      {jobs.length === 0 && !loading && !error && <p className="text-gray-600">No jobs found. Submit a new job to get started!</p>}

      {jobs.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Job ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Solver Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Updated At</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600 hover:underline">
                    <Link to={`/jobs/${job.id}`}>{job.id.substring(0, 8)}...</Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.status}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{job.solver_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(job.created_at).toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(job.updated_at).toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Link to={`/jobs/${job.id}`} className="text-indigo-600 hover:text-indigo-900">View Details</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {hasMore && !loading && (
        <div className="mt-6 text-center">
          <button onClick={handleLoadMore} className="btn-secondary">
            Load More
          </button>
        </div>
      )}

      {loading && jobs.length > 0 && <p className="text-gray-600 mt-4 text-center">Loading more jobs...</p>}
    </div>
  );
};

export default JobList;
