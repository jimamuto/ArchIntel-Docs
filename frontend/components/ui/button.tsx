import * as React from "react"
import { cn } from "@/lib/utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "ghost" | "link" | "outline" | "destructive"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    const baseClasses =
      "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-aurora-purple focus-visible:ring-offset-2 focus-visible:ring-offset-[#0A0C10] disabled:pointer-events-none disabled:opacity-50"

    const variantClasses: Record<NonNullable<ButtonProps["variant"]>, string> = {
      default:
        "bg-primary text-primary-foreground shadow shadow-primary/20 hover:bg-primary/90",
      secondary:
        "bg-secondary text-secondary-foreground hover:bg-secondary/80 border border-white/[0.08]",
      outline:
        "border border-white/[0.1] bg-transparent hover:bg-white/[0.05] text-secondary-foreground",
      ghost:
        "hover:bg-white/[0.05] text-muted-foreground hover:text-foreground",
      link:
        "text-primary underline-offset-4 hover:underline focus:underline",
      destructive:
        "bg-destructive text-destructive-foreground hover:bg-destructive/90"
    }

    const sizeClasses: Record<NonNullable<ButtonProps["size"]>, string> = {
      default: "h-9 px-4 py-2",
      sm: "h-8 rounded-md px-3 text-xs",
      lg: "h-10 rounded-md px-8",
      icon: "h-9 w-9"
    }

    return (
      <button
        ref={ref}
        className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)}
        {...props}
      />
    )
  }
)

Button.displayName = "Button"

export { Button }