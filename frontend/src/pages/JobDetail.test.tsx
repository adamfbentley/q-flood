import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import JobDetail from './JobDetail';
import { useApiKey } from '../context/ApiKeyContext';
import * as jobApi from '../api/jobs';
import { JobStatusEnum } from '../types/job';
import { toast } from 'react-toastify';

// Mock react-router-dom's useParams
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useParams: () => ({ id: 'test-job-id' })
  };
});

// Mock useApiKey context
vi.mock('../context/ApiKeyContext', () => ({
  useApiKey: vi.fn()
}));

// Mock API calls
vi.mock('../api/jobs', () => ({
  getJobDetails: vi.fn(),
  downloadResult: vi.fn()
}));

// Mock react-toastify
vi.mock('react-toastify', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn()
  }
}));

// Mock FloodMap3D component
vi.mock('../components/FloodMap3D', () => ({
  __esModule: true,
  default: vi.fn(() => <div data-testid="floodmap3d-mock">3D Flood Map</div>)
}));

describe('JobDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useApiKey as vi.Mock).mockReturnValue({ apiKey: 'test-api-key' });
    vi.stubEnv('VITE_MAPBOX_ACCESS_TOKEN', 'test-token'); // Ensure mapbox token is set for FloodMap3D
  });

  it('displays loading state initially', () => {
    (jobApi.getJobDetails as vi.Mock).mockReturnValue(new Promise(() => {})); // Never resolve
    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText(/Loading job details.../i)).toBeInTheDocument();
  });

  it('displays error if API Key is not set', async () => {
    (useApiKey as vi.Mock).mockReturnValue({ apiKey: null });
    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );
    await waitFor(() => {
      expect(screen.getByText(/API Key is not set/i)).toBeInTheDocument();
    });
  });

  it('fetches and displays job details', async () => {
    const mockJob = {
      id: 'test-job-id',
      status: JobStatusEnum.COMPLETED,
      solver_type: 'CLASSICAL',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parameters: { param1: 'value1' },
      geojson_path: null,
      pdf_report_path: null
    };
    (jobApi.getJobDetails as vi.Mock).mockResolvedValue(mockJob);

    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Job Details: test-job/i)).toBeInTheDocument();
      expect(screen.getByText(/Status: COMPLETED/i)).toBeInTheDocument();
      expect(screen.getByText(/Solver Type: CLASSICAL/i)).toBeInTheDocument();
    });
  });

  it('fetches and displays FloodMap3D for completed jobs with geojson_path', async () => {
    const mockJob = {
      id: 'test-job-id',
      status: JobStatusEnum.COMPLETED,
      solver_type: 'CLASSICAL',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parameters: { param1: 'value1' },
      geojson_path: 'path/to/geojson',
      pdf_report_path: null
    };
    const mockGeojsonBlob = new Blob([JSON.stringify({ type: 'FeatureCollection', features: [] })], { type: 'application/json' });
    (jobApi.getJobDetails as vi.Mock).mockResolvedValue(mockJob);
    (jobApi.downloadResult as vi.Mock).mockResolvedValue(mockGeojsonBlob);

    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('floodmap3d-mock')).toBeInTheDocument();
    });
    expect(jobApi.downloadResult).toHaveBeenCalledWith('test-job-id', 'geojson', 'test-api-key');
  });

  it('shows a toast error if GeoJSON parsing fails', async () => {
    const mockJob = {
      id: 'test-job-id',
      status: JobStatusEnum.COMPLETED,
      solver_type: 'CLASSICAL',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parameters: { param1: 'value1' },
      geojson_path: 'path/to/geojson',
      pdf_report_path: null
    };
    const malformedGeojsonBlob = new Blob(['{invalid json'], { type: 'application/json' });
    (jobApi.getJobDetails as vi.Mock).mockResolvedValue(mockJob);
    (jobApi.downloadResult as vi.Mock).mockResolvedValue(malformedGeojsonBlob);

    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to load GeoJSON data for visualization.');
    });
    expect(screen.queryByTestId('floodmap3d-mock')).not.toBeInTheDocument();
  });

  it('handles download of geojson file', async () => {
    const mockJob = {
      id: 'test-job-id',
      status: JobStatusEnum.COMPLETED,
      solver_type: 'CLASSICAL',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parameters: { param1: 'value1' },
      geojson_path: 'path/to/geojson',
      pdf_report_path: null
    };
    const mockGeojsonBlob = new Blob(['{}'], { type: 'application/json' });
    (jobApi.getJobDetails as vi.Mock).mockResolvedValue(mockJob);
    (jobApi.downloadResult as vi.Mock).mockResolvedValue(mockGeojsonBlob);

    // Mock URL.createObjectURL and URL.revokeObjectURL
    const createObjectURLSpy = vi.spyOn(window.URL, 'createObjectURL').mockReturnValue('blob:http://localhost/mock-url');
    const revokeObjectURLSpy = vi.spyOn(window.URL, 'revokeObjectURL');

    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Download GeoJSON/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Download GeoJSON/i));

    await waitFor(() => {
      expect(jobApi.downloadResult).toHaveBeenCalledWith('test-job-id', 'geojson', 'test-api-key');
      expect(createObjectURLSpy).toHaveBeenCalledWith(mockGeojsonBlob);
      expect(revokeObjectURLSpy).toHaveBeenCalledWith('blob:http://localhost/mock-url');
      expect(toast.success).toHaveBeenCalledWith('Successfully downloaded geojson file.');
    });
  });

  it('shows error toast if download fails', async () => {
    const mockJob = {
      id: 'test-job-id',
      status: JobStatusEnum.COMPLETED,
      solver_type: 'CLASSICAL',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parameters: { param1: 'value1' },
      geojson_path: 'path/to/geojson',
      pdf_report_path: null
    };
    (jobApi.getJobDetails as vi.Mock).mockResolvedValue(mockJob);
    (jobApi.downloadResult as vi.Mock).mockRejectedValue(new Error('Network error'));

    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Download GeoJSON/i)).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText(/Download GeoJSON/i));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to download geojson: Network error');
    });
  });

  // Test polling logic - this is more complex and might require fake timers
  it('polls for job status until completion', async () => {
    vi.useFakeTimers();

    const jobPending = {
      id: 'test-job-id',
      status: JobStatusEnum.RUNNING,
      solver_type: 'CLASSICAL',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      parameters: {},
      geojson_path: null,
      pdf_report_path: null
    };
    const jobCompleted = {
      ...jobPending,
      status: JobStatusEnum.COMPLETED,
      updated_at: new Date().toISOString()
    };

    (jobApi.getJobDetails as vi.Mock)
      .mockResolvedValueOnce(jobPending) // First fetch
      .mockResolvedValueOnce(jobPending) // Second fetch after 5s
      .mockResolvedValueOnce(jobCompleted); // Third fetch after 10s

    render(
      <MemoryRouter initialEntries={['/jobs/test-job-id']}>
        <Routes>
          <Route path="/jobs/:id" element={<JobDetail />} />
        </Routes>
      </MemoryRouter>
    );

    // Initial fetch
    await waitFor(() => expect(screen.getByText(/Status: RUNNING/i)).toBeInTheDocument());
    expect(jobApi.getJobDetails).toHaveBeenCalledTimes(1);

    // Advance timers by 5 seconds, expect another fetch
    vi.advanceTimersByTime(5000);
    await waitFor(() => expect(jobApi.getJobDetails).toHaveBeenCalledTimes(2));
    expect(screen.getByText(/Status: RUNNING/i)).toBeInTheDocument(); // Still running

    // Advance timers by another 5 seconds, expect completion and no more fetches
    vi.advanceTimersByTime(5000);
    await waitFor(() => expect(jobApi.getJobDetails).toHaveBeenCalledTimes(3));
    await waitFor(() => expect(screen.getByText(/Status: COMPLETED/i)).toBeInTheDocument());

    // Advance timers again, ensure no more fetches
    vi.advanceTimersByTime(5000);
    expect(jobApi.getJobDetails).toHaveBeenCalledTimes(3); // Should not be called again

    vi.useRealTimers();
  });
});
