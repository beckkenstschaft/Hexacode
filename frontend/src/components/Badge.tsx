/** Badge component */

import { HTMLAttributes, forwardRef } from "react";
import { clsx } from "clsx";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "success" | "warning" | "danger" | "info" | "simulated";
  size?: "sm" | "md";
  dot?: boolean;
}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant = "default", size = "md", dot = false, children, ...props }, ref) => {
    const variantStyles = {
      default: "bg-gray-100 text-gray-700",
      success: "bg-green-100 text-green-700",
      warning: "bg-yellow-100 text-yellow-700",
      danger: "bg-red-100 text-red-700",
      info: "bg-blue-100 text-blue-700",
      simulated: "bg-purple-100 text-purple-700 border border-purple-200",
    };

    const sizeStyles = {
      sm: "px-2 py-0.5 text-xs",
      md: "px-2.5 py-1 text-sm",
    };

    return (
      <span
        ref={ref}
        className={clsx(
          "inline-flex items-center gap-1 font-medium rounded-full",
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      >
        {dot && (
          <span
            className={clsx("w-1.5 h-1.5 rounded-full", {
              "bg-gray-400": variant === "default",
              "bg-green-500": variant === "success",
              "bg-yellow-500": variant === "warning",
              "bg-red-500": variant === "danger",
              "bg-blue-500": variant === "info",
              "bg-purple-500": variant === "simulated",
            })}
            aria-hidden="true"
          />
        )}
        {children}
      </span>
    );
  }
);

Badge.displayName = "Badge";