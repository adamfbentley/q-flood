export enum JobStatusEnum {
  PENDING = 'PENDING',
  RUNNING = 'RUNNING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELLED = 'CANCELLED',
  QUANTUM_FAILED_FALLBACK_INITIATED = 'QUANTUM_FAILED_FALLBACK_INITIATED',
  FALLBACK_CLASSICAL_RUNNING = 'FALLBACK_CLASSICAL_RUNNING',
  FALLBACK_CLASSICAL_COMPLETED = 'FALLBACK_CLASSICAL_COMPLETED',
  FALLBACK_CLASSICAL_FAILED = 'FALLBACK_CLASSICAL_FAILED',
}

export enum SolverTypeEnum {
  CLASSICAL = 'CLASSICAL',
  QUANTUM = 'QUANTUM',
  HYBRID = 'HYBRID',
}

export interface JobBase {
  solver_type: SolverTypeEnum;
  parameters?: Record<string, any> | null;
  input_data_path?: string | null;
}

export interface JobCreate extends JobBase {}

export interface JobResponse extends JobBase {
  id: string;
  status: JobStatusEnum;
  matrix_path?: string | null;
  vector_path?: string | null;
  solution_path?: string | null;
  geojson_path?: string | null;
  pdf_report_path?: string | null;
  fallback_reason?: string | null;
  created_at: string;
  updated_at: string;
}
