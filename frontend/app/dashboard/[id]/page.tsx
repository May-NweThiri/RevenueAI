"use client"

import { useRef, useState } from "react"
import { useParams } from "next/navigation"
import Link from "next/link"
import { useDataset } from "@/hooks/use-dataset"
import { useMetrics } from "@/hooks/use-metrics"
import { useInsights } from "@/hooks/use-insights"
import { GlassCard } from "@/components/shared/glass-card"
import {
  LoadingPage,
  LoadingSpinner,
} from "@/components/shared/loading-spinner"
import { MetricsGrid } from "@/components/dashboard/metrics-grid"
import { SummaryCard } from "@/components/dashboard/summary-card"
import {
  RevenueTrendChart,
  CategoryPieChart,
  TopProductsBarChart,
  GrowthRateChart,
} from "@/components/dashboard/charts"
import { downloadReportPdf } from "@/lib/export-report"
import { BrandName } from "@/components/shared/brand-name"
import { formatDate, getSeverityColor, timeAgo } from "@/lib/utils"
import { MessageSquare, Table, Lightbulb, Download } from "lucide-react"

export default function DatasetDetailPage() {
  const params = useParams()
  const id = params.id as string
  const { dataset, loading: dsLoading, error: dsError } = useDataset(id)
  const { metrics, loading: mLoading, error: mError } = useMetrics(id)
  const { insights, loading: iLoading } = useInsights(id)

  const reportRef = useRef<HTMLDivElement | null>(null)
  const [exporting, setExporting] = useState(false)

  async function handleDownload() {
    if (!reportRef.current || !dataset) return
    setExporting(true)
    try {
      await downloadReportPdf(reportRef.current, dataset.name)
    } catch (err) {
      console.error("Export failed:", err)
      window.alert("Could not generate the report. Please try again.")
    } finally {
      setExporting(false)
    }
  }

  if (dsLoading) return <LoadingPage />

  if (dsError || !dataset) {
    return (
      <div className="flex items-center justify-center py-20">
        <p className="text-sm text-red-400">
          Error: {dsError || "Dataset not found"}
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6 py-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">
            {dataset.name}
          </h2>
          <p className="mt-1 text-sm text-foreground/40">
            {dataset.row_count} rows &middot; {dataset.column_count} columns
            &middot; uploaded {timeAgo(dataset.created_at)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleDownload}
            disabled={exporting || mLoading}
            className="flex items-center gap-1.5 rounded-lg border border-surface-border bg-surface-card px-4 py-2 text-sm font-medium text-foreground/80 transition-colors hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Download className="h-4 w-4" />
            {exporting ? "Preparing..." : "Download"}
          </button>
          <Link
            href={`/dashboard/${id}/chat`}
            className="flex items-center gap-1.5 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-hover"
          >
            <MessageSquare className="h-4 w-4" />
            AI Chat
          </Link>
        </div>
      </div>

      <div ref={reportRef} className="space-y-6 bg-surface">
        <div className="flex items-center justify-between border-b border-surface-border pb-4">
          <BrandName className="text-base" />
          <p className="text-xs text-foreground/30">
            Report generated {formatDate(new Date().toISOString())}
          </p>
        </div>

      {mLoading ? (
        <LoadingSpinner className="py-12" />
      ) : mError ? (
        <p className="text-sm text-red-400">Error loading metrics: {mError}</p>
      ) : metrics ? (
        <>
          <MetricsGrid metrics={metrics} />

          <RevenueTrendChart metrics={metrics} />

          <div className="grid gap-4 lg:grid-cols-2">
            <CategoryPieChart metrics={metrics} />
            <TopProductsBarChart metrics={metrics} />
          </div>

          <GrowthRateChart metrics={metrics} />

          <SummaryCard datasetId={id} />
        </>
      ) : null}

      {dataset.columns_meta && dataset.columns_meta.length > 0 && (
        <GlassCard>
          <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-foreground/70">
            <Table className="h-4 w-4" />
            Columns Detected
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border text-left text-xs text-foreground/40">
                  <th className="pb-2 font-medium">Column</th>
                  <th className="pb-2 font-medium">Type</th>
                  <th className="pb-2 font-medium">Detected Role</th>
                  <th className="pb-2 font-medium">Sample Values</th>
                </tr>
              </thead>
              <tbody>
                {dataset.columns_meta.map((col) => (
                  <tr
                    key={col.name}
                    className="border-b border-surface-border/50 text-foreground/70"
                  >
                    <td className="py-2.5 font-medium text-foreground/90">
                      {col.name}
                    </td>
                    <td className="py-2.5 text-foreground/50">{col.dtype}</td>
                    <td className="py-2.5">
                      <span className="rounded-md bg-accent/10 px-2 py-0.5 text-xs text-accent">
                        {col.detected_role}
                      </span>
                    </td>
                    <td className="py-2.5 text-foreground/50">
                      {col.sample_values?.slice(0, 3).join(", ")}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </GlassCard>
      )}

      {iLoading ? (
        <LoadingSpinner className="py-8" />
      ) : insights.length > 0 ? (
        <GlassCard>
          <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-foreground/70">
            <Lightbulb className="h-4 w-4" />
            AI Insights
          </h3>
          <div className="space-y-3">
            {insights.map((insight) => (
              <div
                key={insight.id}
                className={`rounded-lg border-l-2 p-4 ${getSeverityColor(insight.severity)}`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-foreground/90">
                      {insight.title}
                    </p>
                    <p className="mt-1 text-xs text-foreground/50">
                      {insight.content}
                    </p>
                  </div>
                  <span className="shrink-0 rounded-full bg-foreground/5 px-2 py-0.5 text-[10px] uppercase tracking-wider text-foreground/40">
                    {insight.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      ) : null}
      </div>
    </div>
  )
}
