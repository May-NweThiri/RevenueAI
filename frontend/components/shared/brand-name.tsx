import { cn } from "@/lib/utils"

export function BrandName({ className }: { className?: string }) {
  return (
    <span className={cn("font-semibold tracking-tight", className)}>
      <span className="text-gradient">FinX</span>
      <span className="text-foreground/60"> AI</span>
    </span>
  )
}
