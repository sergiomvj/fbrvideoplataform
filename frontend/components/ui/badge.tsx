import { type HTMLAttributes, forwardRef } from "react";
import { type StateVariant } from "@/lib/design-system/tokens";

type BadgeVariant = StateVariant | "neutral";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  success: "bg-green-50 text-green-700 border-green-200",
  warning: "bg-amber-50 text-amber-700 border-amber-200",
  danger: "bg-red-50 text-red-700 border-red-200",
  info: "bg-cyan-50 text-cyan-700 border-cyan-200",
  neutral: "bg-gray-100 text-gray-700 border-gray-200",
};

const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ variant = "neutral", className = "", ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={[
          "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
          "transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2",
          variantClasses[variant],
          className,
        ].join(" ")}
        {...props}
      />
    );
  }
);

Badge.displayName = "Badge";

export { Badge, type BadgeProps, type BadgeVariant };
