export interface RankedItem {
  name: string
  value: number
}

export interface DatasetSummary {
  overview: string[]
  top_products: RankedItem[]
  low_products: RankedItem[]
  top_customers: RankedItem[]
  top_regions: RankedItem[]
  low_regions: RankedItem[]
  region_column: string | null
  advice: string[]
  data_quality: string[]
}
