import * as React from "react"
import { cn } from "@/lib/utils"

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-gradient-to-r from-slate-800/30 via-slate-800/50 to-slate-800/30 bg-[length:200%_100%]",
        className
      )}
      style={{
        animation: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite, gradient 3s ease infinite",
      }}
      {...props}
    />
  )
}

export { Skeleton }