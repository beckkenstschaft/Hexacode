/** Input component */

import { forwardRef, InputHTMLAttributes, LabelHTMLAttributes } from "react";
import { clsx } from "clsx";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className={clsx("block text-sm font-medium text-snapdragon-navy mb-1.5", label && "required")}
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={clsx(
            "w-full px-3 py-2 rounded-lg border bg-white text-snapdragon-navy placeholder-gray-400",
            "focus:outline-none focus:ring-2 focus:ring-snapdragon-blue focus:border-transparent",
            "disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed",
            error && "border-red-500 focus:ring-red-500",
            !error && "border-gray-300 hover:border-gray-400",
            className
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={`${inputId}-hint`} className="mt-1.5 text-sm text-gray-500">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export const Textarea = forwardRef<HTMLTextAreaElement, InputProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={inputId}
            className={clsx("block text-sm font-medium text-snapdragon-navy mb-1.5")}
          >
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={clsx(
            "w-full px-3 py-2 rounded-lg border bg-white text-snapdragon-navy placeholder-gray-400 resize-y min-h-[100px]",
            "focus:outline-none focus:ring-2 focus:ring-snapdragon-blue focus:border-transparent",
            "disabled:bg-gray-50 disabled:text-gray-500 disabled:cursor-not-allowed",
            error && "border-red-500 focus:ring-red-500",
            !error && "border-gray-300 hover:border-gray-400",
            className
          )}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} className="mt-1.5 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        {hint && !error && (
          <p id={`${inputId}-hint`} className="mt-1.5 text-sm text-gray-500">
            {hint}
          </p>
        )}
      </div>
    );
  }
);

Textarea.displayName = "Textarea";

export const Label = forwardRef<HTMLLabelElement, LabelHTMLAttributes<HTMLLabelElement>>(
  ({ className, children, ...props }, ref) => (
    <label
      ref={ref}
      className={clsx("block text-sm font-medium text-snapdragon-navy mb-1.5", className)}
      {...props}
    >
      {children}
    </label>
  )
);

Label.displayName = "Label";