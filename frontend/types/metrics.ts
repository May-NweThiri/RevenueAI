export interface Metric {
  id: string
  dataset_id: string
  metric_type: string
  metric_name: string
  value: number
  currency: string | null
  period: string | null
  rank: number | null
  created_at: string
}

export interface MetricsGroupedResponse {
  total_revenue: Metric[]
  monthly_revenue: Metric[]
  growth_rate: Metric[]
  average_order_value: Metric[]
  top_products: Metric[]
  category_breakdown: Metric[]
  trends: Metric[]
}
