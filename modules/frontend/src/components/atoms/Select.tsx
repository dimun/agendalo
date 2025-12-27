import type { SelectHTMLAttributes, ReactNode } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  children: ReactNode;
  error?: string;
}

export function Select({ error, children, className = '', ...props }: SelectProps) {
  const errorClasses = error
    ? 'border-red-500 focus:ring-red-500 focus:border-red-500'
    : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500';

  return (
    <div>
      <select
        className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-1 ${errorClasses} ${className}`}
        {...props}
      >
        {children}
      </select>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
}

