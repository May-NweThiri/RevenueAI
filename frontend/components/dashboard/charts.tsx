"use client"

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { formatCurrency, formatPercent } from "@/lib/utils"
import type { MetricsGroupedResponse } from "@/types/metrics"

const COLORS = [
  "#6366f1",
  "#8b5cf6",
  "#a78bfa",
  "#22d3ee",
  "#34d399",
  "#fbbf24",
  "#f472b6",
]

function ChartTooltip({
  active,
  payload,
  label,
  valueFormatter,
}: {
  active?: boolean
  payload?: { value: number; name?: string; payload?: { name?: string } }[]
  label?: string
  valueFormatter?: (v: number) => string
}) {
  if (!active || !payload?.length) return null
  const value = payload[0].value
  return (
    <div className="rounded-lg border border-surface-border bg-surface/95 px-3 py-2 text-xs shadow-lg backdrop-blur">
      <p className="text-foreground/50">{label || payload[0].payload?.name}</p>
      <p className="font-medium text-foreground">
        {valueFormatter ? valueFormatter(value) : value}
      </p>
    </div>
  )
}

export function RevenueTrendChart({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const monthly = [...(metrics.monthly_revenue || [])].sort((a, b) =>
    (a.period || "").localeCompare(b.period || ""),
  )
  if (!monthly.length) return null

  const data = monthly.map((m) => ({
    period: m.period || m.metric_name,
    revenue: m.value,
  }))

  return (
    <div className="glass h-[320px] rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Monthly Revenue Trend
      </h3>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.35} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis
            dataKey="period"
            tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            interval="equidistantPreserveStart"
          />
          <YAxis
            tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
          />
          <Tooltip content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />} />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#revenueGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function CategoryPieChart({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const categories = metrics.category_breakdown || []
  if (!categories.length) return null

  const data = categories.map((c) => ({
    name: c.metric_name,
    value: c.value,
  }))

  return (
    <div className="glass h-[320px] rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Revenue by Category
      </h3>
      <ResponsiveContainer width="100%" height="85%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={90}
            paddingAngle={2}
          >
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip valueFormatter={(v) => formatCurrency(v)} />} />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-2 flex flex-wrap justify-center gap-3">
        {data.slice(0, 5).map((d, i) => (
          <div key={d.name} className="flex items-center gap-1.5 text-[11px] text-foreground/50">
            <span
              className="h-2 w-2 rounded-full"
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            />
            {d.name}
          </div>
        ))}
      </div>
    </div>
  )
}

export function TopProductsBarChart({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const products = [...(metrics.top_products || [])]
    .sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
    .slice(0, 8)
  if (!products.length) return null

  const data = products.map((p) => ({
    name:
      p.metric_name.length > 18
        ? `${p.metric_name.slice(0, 16)}…`
        : p.metric_name,
    fullName: p.metric_name,
    revenue: p.value,
  }))

  return (
    <div className="glass h-[320px] rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Top Products
      </h3>
      <ResponsiveContainer width="100%" height="85%">
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `$${(v / 1000).toFixed(0)}k`}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={90}
            tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            content={
              <ChartTooltip
                valueFormatter={(v) => formatCurrency(v)}
              />
            }
          />
          <Bar dataKey="revenue" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function GrowthRateChart({
  metrics,
}: {
  metrics: MetricsGroupedResponse
}) {
  const growth = (metrics.growth_rate || []).filter(
    (g) => g.period && g.period !== "all",
  )
  if (!growth.length) return null

  const data = growth.map((g) => ({
    period: g.period,
    growth: g.value,
  }))

  return (
    <div className="glass h-[280px] rounded-xl p-5">
      <h3 className="mb-4 text-sm font-medium text-foreground/70">
        Month-over-Month Growth
      </h3>
      <ResponsiveContainer width="100%" height="80%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
          <XAxis
            dataKey="period"
            tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip content={<ChartTooltip valueFormatter={(v) => formatPercent(v)} />} />
          <Bar dataKey="growth" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.growth >= 0 ? "#34d399" : "#f87171"}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
