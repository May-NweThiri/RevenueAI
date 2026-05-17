import { cn } from "@/lib/utils"

interface GlassCardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}

export function GlassCard({ children, className, hover }: GlassCardProps) {
  return (
    <div
      className={cn(
        "glass rounded-xl p-5",
        hover && "glass-hover cursor-pointer",
        className,
      )}
    >
      {children}
    </div>
  )
}
