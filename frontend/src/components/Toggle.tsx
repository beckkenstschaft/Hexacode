/** Toggle switch component */

import { forwardRef, InputHTMLAttributes } from "react";
import { clsx } from "clsx";

interface ToggleProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label?: string;
  description?: string;
}

export const Toggle = forwardRef<HTMLInputElement, ToggleProps>(
  ({ className, label, description, id, disabled, ...props }, ref) => {
    const toggleId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className={clsx("flex items-start gap-3", className)}>
        <div className="relative flex items-center">
          <input
            ref={ref}
            type="checkbox"
            id={toggleId}
            className={clsx(
              "peer h-5 w-5 cursor-pointer appearance-none rounded-full border-2",
              "bg-gray-200 border-gray-300",
              "checked:bg-snapdragon-blue checked:border-snapdragon-blue",
              "focus:outline-none focus:ring-2 focus:ring-snapdragon-blue focus:ring-offset-2",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              "transition-colors duration-200"
            )}
            disabled={disabled}
            {...props}
          />
          <span className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <svg
              className="w-3.5 h-3.5 text-white opacity-0 peer-checked:opacity-100 transition-opacity"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </span>
        </div>
        <div className="pt-1">
          {label && (
            <label
              htmlFor={toggleId}
              className={clsx("block text-sm font-medium text-snapdragon-navy cursor-pointer", disabled && "opacity-50")}
            >
              {label}
            </label>
          )}
          {description && (
            <p className="text-sm text-gray-500 mt-0.5">{description}</p>
          )}
        </div>
      </div>
    );
  }
);

Toggle.displayName = "Toggle";