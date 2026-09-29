/** Loading and empty state components */

import { clsx } from "clsx";

interface LoadingProps {
  size?: "sm" | "md" | "lg";
  className?: string;
  text?: string;
}

export function Loading({ size = "md", className, text }: LoadingProps) {
  const sizeStyles = {
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  return (
    <div className={clsx("flex flex-col items-center justify-center gap-3", className)}>
      <svg
        className={clsx("animate-spin text-snapdragon-blue", sizeStyles[size])}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      {text && <p className="text-sm text-gray-500">{text}</p>}
    </div>
  );
}

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export function EmptyState({ icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={clsx("flex flex-col items-center justify-center text-center py-12 px-4", className)}>
      {icon && <div className="text-gray-300 mb-4">{icon}</div>}
      <h3 className="text-lg font-medium text-snapdragon-navy mb-2">{title}</h3>
      {description && <p className="text-gray-500 mb-6 max-w-md">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

interface ErrorStateProps {
  title: string;
  message: string;
  onRetry?: () => void;
  retryLabel?: string;
  className?: string;
}

export function ErrorState({ title, message, onRetry, retryLabel = "Try again", className }: ErrorStateProps) {
  return (
    <div className={clsx("flex flex-col items-center justify-center text-center py-12 px-4", className)}>
      <div className="text-red-500 mb-4">
        <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 className="text-lg font-medium text-snapdragon-navy mb-2">{title}</h3>
      <p className="text-gray-500 mb-6 max-w-md">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-2 bg-snapdragon-blue text-white rounded-lg hover:bg-snapdragon-blue-hover transition-colors"
        >
          {retryLabel}
        </button>
      )}
    </div>
  );
}