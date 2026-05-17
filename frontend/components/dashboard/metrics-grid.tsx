import { DollarSign, Package, ShoppingCart, TrendingUp } from "lucide-react"
import { KPICard } from "./kpi-card"
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils"
import type { MetricsGroupedResponse } from "@/types/metrics"

interface MetricsGridProps {
  metrics: MetricsGroupedResponse
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  const totalRevenue = metrics.total_revenue?.[0]
  const aov = metrics.average_order_value?.[0]
  const growth = metrics.growth_rate?.[0]
  const topProduct = metrics.top_products?.[0]

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <KPICard
        title="Total Revenue"
        value={
          totalRevenue
            ? formatCurrency(totalRevenue.value, totalRevenue.currency || undefined)
            : "—"
        }
        subtitle={
          totalRevenue?.period && totalRevenue.period !== "all"
            ? `as of ${totalRevenue.period}`
            : undefined
        }
        trend={growth ? growth.value : undefined}
        icon={<DollarSign className="h-5 w-5" />}
      />
      <KPICard
        title="Growth Rate"
        value={growth ? formatPercent(growth.value) : "—"}
        subtitle={growth?.period ? `over ${growth.period}` : undefined}
        icon={<TrendingUp className="h-5 w-5" />}
      />
      <KPICard
        title="Avg Order Value"
        value={aov ? formatCurrency(aov.value) : "—"}
        icon={<ShoppingCart className="h-5 w-5" />}
      />
      <KPICard
        title="Top Product"
        value={topProduct ? topProduct.metric_name : "—"}
        subtitle={
          topProduct ? formatCurrency(topProduct.value) : undefined
        }
        icon={<Package className="h-5 w-5" />}
      />
    </div>
  )
}

export function MonthlyRevenueTable({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const monthly = metrics.monthly_revenue || []
  if (!monthly.length) return null

  return (
    <div className="glass rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Monthly Revenue
      </h3>
      <div className="space-y-2">
        {monthly.map((m) => (
          <div
            key={m.id}
            className="flex items-center justify-between rounded-lg bg-surface-card px-4 py-2.5"
          >
            <span className="text-sm text-foreground/60">{m.period}</span>
            <span className="text-sm font-medium">
              {formatCurrency(m.value)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

export function CategoryBreakdown({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const categories = metrics.category_breakdown || []
  if (!categories.length) return null

  const total = categories.reduce((sum, c) => sum + c.value, 0)

  return (
    <div className="glass rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Category Breakdown
      </h3>
      <div className="space-y-3">
        {categories.map((c) => {
          const pct = total > 0 ? ((c.value / total) * 100).toFixed(1) : "0"
          return (
            <div key={c.id}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="text-foreground/80">{c.metric_name}</span>
                <span className="font-medium">
                  {formatCurrency(c.value)}
                  <span className="ml-1.5 text-xs text-foreground/40">
                    ({pct}%)
                  </span>
                </span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-surface-border">
                <div
                  className="h-full rounded-full bg-accent transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function TopProducts({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const products = metrics.top_products || []
  if (!products.length) return null

  return (
    <div className="glass rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Top Products
      </h3>
      <div className="space-y-1">
        {products.map((p, i) => (
          <div
            key={p.id}
            className="flex items-center justify-between rounded-lg px-3 py-2 text-sm hover:bg-surface-hover"
          >
            <div className="flex items-center gap-3">
              <span className="flex h-6 w-6 items-center justify-center rounded-md bg-accent/10 text-xs font-medium text-accent">
                {i + 1}
              </span>
              <span className="text-foreground/80">{p.metric_name}</span>
            </div>
            <span className="font-medium">
              {formatCurrency(p.value, p.currency || undefined)}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
