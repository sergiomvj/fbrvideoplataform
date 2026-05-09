import { type HTMLAttributes, forwardRef } from "react";
import { type StateVariant } from "@/lib/design-system/tokens";

interface StatusIndicatorProps extends HTMLAttributes<HTMLSpanElement> {
  state: StateVariant;
  label?: string;
  pulse?: boolean;
}

const dotColor: Record<StateVariant, string> = {
  success: "bg-green-500",
  warning: "bg-amber-500",
  danger: "bg-red-500",
  info: "bg-cyan-500",
};

const StatusIndicator = forwardRef<HTMLSpanElement, StatusIndicatorProps>(
  ({ state, label, pulse = false, className = "", ...props }, ref) => {
    return (
      <span
        ref={ref}
        role="status"
        aria-label={label ?? `Status: ${state}`}
        className={["inline-flex items-center gap-2 text-sm", className].join(" ")}
        {...props}
      >
        <span
          aria-hidden="true"
          className={[
            "inline-block h-2.5 w-2.5 rounded-full",
            dotColor[state],
            pulse && "animate-pulse",
          ]
            .filter(Boolean)
            .join(" ")}
        />
        {label && <span>{label}</span>}
      </span>
    );
  }
);

StatusIndicator.displayName = "StatusIndicator";

export { StatusIndicator, type StatusIndicatorProps };
