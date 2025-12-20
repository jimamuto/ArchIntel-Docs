import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "../../lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:ring-offset-2 focus:ring-offset-slate-950",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 shadow-md shadow-cyan-500/20",
        secondary:
          "border-transparent bg-slate-800/50 text-slate-200 hover:bg-slate-700/50",
        destructive:
          "border-transparent bg-gradient-to-r from-rose-600 to-rose-700 text-slate-50 shadow-md shadow-rose-500/20",
        outline:
          "border border-slate-700/50 bg-transparent text-slate-300 hover:border-cyan-500/50 hover:text-cyan-300",
        success:
          "border-transparent bg-gradient-to-r from-emerald-500 to-emerald-600 text-slate-950 shadow-md shadow-emerald-500/20",
        warning:
          "border-transparent bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 shadow-md shadow-amber-500/20",
        info:
          "border-transparent bg-gradient-to-r from-cyan-500 to-cyan-600 text-slate-950 shadow-md shadow-cyan-500/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }