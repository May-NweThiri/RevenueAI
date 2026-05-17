"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"
import type { MetricsGroupedResponse } from "@/types/metrics"

export function useMetrics(datasetId: string) {
  const [metrics, setMetrics] = useState<MetricsGroupedResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!datasetId) return
    api
      .getMetrics(datasetId)
      .then(setMetrics)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [datasetId])

  return { metrics, loading, error }
}
