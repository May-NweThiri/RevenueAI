export interface Insight {
  id: string
  dataset_id: string
  type: string
  title: string
  content: string
  severity: string
  created_at: string
}

export interface InsightListResponse {
  insights: Insight[]
  total: number
}
