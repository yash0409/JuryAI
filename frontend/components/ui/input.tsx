import * as React from "react"
import { Input as InputPrimitive } from "@base-ui/react/input"

import { cn } from "@/lib/utils"

function Input({ className, type, ...props }: React.ComponentProps<"input">) {
  return (
    <InputPrimitive
      type={type}
      data-slot="input"
      className={cn(
        "h-10 w-full min-w-0 rounded-xl border border-[rgba(255,255,255,0.1)] bg-[rgba(255,255,255,0.05)] px-3 py-2 text-sm text-white transition-colors outline-none placeholder:text-[#94a3b8] focus-visible:border-[#3b82f6] focus-visible:ring-2 focus-visible:ring-[#3b82f6]/25 disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-[rgba(255,255,255,0.06)] disabled:opacity-60 aria-invalid:border-[#ef4444] aria-invalid:ring-2 aria-invalid:ring-[#ef4444]/20",
        className
      )}
      {...props}
    />
  )
}

export { Input }
