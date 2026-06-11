export interface Metric {
  id: string
  dataset_id: string
  metric_type: string
  metric_name: string
  value: number
  currency: string | null
  period: string | null
  rank: number | null
  extra_metadata?: Record<string, unknown> | null
  created_at: string
}

export interface MetricsGroupedResponse {
  dataset_id?: string
  total_revenue: Metric[]
  monthly_revenue: Metric[]
  growth_rate: Metric[]
  aov: Metric[]
  top_products: Metric[]
  category_breakdown: Metric[]
  trends: Metric[]
  other?: Metric[]
}
