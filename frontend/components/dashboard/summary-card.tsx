"use client"

import { GlassCard } from "@/components/shared/glass-card"
import { LoadingSpinner } from "@/components/shared/loading-spinner"
import { useSummary } from "@/hooks/use-summary"
import type { RankedItem } from "@/types/summary"
import {
  FileText,
  TrendingUp,
  TrendingDown,
  Users,
  MapPin,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react"

function money(value: number): string {
  return `$${value.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function RankedList({
  title,
  icon,
  items,
  accent,
}: {
  title: string
  icon: React.ReactNode
  items: RankedItem[]
  accent?: "up" | "down"
}) {
  if (items.length === 0) return null
  return (
    <div className="rounded-lg border border-surface-border bg-surface-card/50 p-4">
      <p className="mb-3 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wider text-foreground/40">
        {icon}
        {title}
      </p>
      <ol className="space-y-2">
        {items.map((item, i) => (
          <li key={item.name} className="flex items-center justify-between gap-2 text-sm">
            <span className="truncate text-foreground/80">
              <span className="mr-1.5 text-foreground/30">{i + 1}.</span>
              {item.name}
            </span>
            <span
              className={`shrink-0 font-medium ${
                accent === "down" ? "text-red-400/80" : "text-foreground/90"
              }`}
            >
              {money(item.value)}
            </span>
          </li>
        ))}
      </ol>
    </div>
  )
}

export function SummaryCard({ datasetId }: { datasetId: string }) {
  const { summary, loading, error } = useSummary(datasetId)

  if (loading) return <LoadingSpinner className="py-8" />
  if (error || !summary) return null

  const regionLabel = summary.region_column || "Region"

  return (
    <GlassCard>
      <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-foreground/70">
        <FileText className="h-4 w-4" />
        Executive Summary
      </h3>

      <div className="space-y-2">
        {summary.overview.map((line) => (
          <p key={line} className="text-sm leading-relaxed text-foreground/70">
            {line}
          </p>
        ))}
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <RankedList
          title="Top Products"
          icon={<TrendingUp className="h-3.5 w-3.5" />}
          items={summary.top_products}
        />
        <RankedList
          title="Lowest-Selling Products"
          icon={<TrendingDown className="h-3.5 w-3.5" />}
          items={summary.low_products}
          accent="down"
        />
        <RankedList
          title="Top Customers"
          icon={<Users className="h-3.5 w-3.5" />}
          items={summary.top_customers}
        />
        <RankedList
          title={`Top ${regionLabel}`}
          icon={<MapPin className="h-3.5 w-3.5" />}
          items={summary.top_regions}
        />
      </div>

      {summary.advice.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-foreground/40">
            Recommendations
          </p>
          <ul className="space-y-2">
            {summary.advice.map((tip) => (
              <li key={tip} className="flex items-start gap-2 text-sm text-foreground/70">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-400/70" />
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {summary.data_quality.length > 0 && (
        <div className="mt-5 rounded-lg border border-amber-500/20 bg-amber-500/5 p-4">
          <p className="mb-2 flex items-center gap-1.5 text-xs font-medium uppercase tracking-wider text-amber-400/80">
            <AlertTriangle className="h-3.5 w-3.5" />
            Data Quality Issues
          </p>
          <ul className="space-y-1.5">
            {summary.data_quality.map((issue) => (
              <li key={issue} className="text-sm text-foreground/60">
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}
    </GlassCard>
  )
}
