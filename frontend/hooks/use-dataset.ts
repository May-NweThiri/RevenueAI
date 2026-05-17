"use client"

import { useEffect, useState } from "react"
import { api } from "@/lib/api-client"
import type { Dataset } from "@/types/dataset"

export function useDatasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .getDatasets()
      .then((res) => setDatasets(res.datasets))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { datasets, loading, error, refetch: () => {} }
}

export function useDataset(id: string) {
  const [dataset, setDataset] = useState<Dataset | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    api
      .getDataset(id)
      .then(setDataset)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  return { dataset, loading, error }
}
