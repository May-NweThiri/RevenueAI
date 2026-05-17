export interface ColumnMeta {
  name: string
  dtype: string
  detected_role: string
  sample_values: unknown[]
}

export interface DatasetSummary {
  row_count: number
  column_count: number
  columns: string[]
  dtypes: Record<string, string>
  missing_values: Record<string, number>
  missing_pct: Record<string, number>
  numeric_columns: string[]
  categorical_columns: string[]
  date_columns: string[]
  memory_usage_mb: number
}

export interface Dataset {
  id: string
  upload_id: string
  name: string
  row_count: number
  column_count: number
  columns_meta: ColumnMeta[]
  summary: DatasetSummary
  file_path: string
  status: string
  error_msg: string | null
  created_at: string
}

export interface DatasetListResponse {
  datasets: Dataset[]
  total: number
}

export interface UploadResponse {
  id: string
  filename: string
  file_type: string
  file_size: number
  row_count: number
  column_count: number
  status: string
  error_msg: string | null
  created_at: string
  dataset_id?: string
}

export interface PreviewResponse {
  columns: string[]
  rows: Record<string, unknown>[]
  total_rows: number
  preview_rows: number
}
