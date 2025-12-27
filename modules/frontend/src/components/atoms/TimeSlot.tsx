import { HTMLAttributes } from 'react';

interface TimeSlotProps extends HTMLAttributes<HTMLDivElement> {
  time: string;
  isHalfHour?: boolean;
}

export function TimeSlot({ time, isHalfHour = false, className = '', ...props }: TimeSlotProps) {
  return (
    <div
      className={`flex items-center justify-center text-xs text-gray-500 ${isHalfHour ? 'h-6' : 'h-12'} border-b border-gray-200 ${className}`}
      {...props}
    >
      {!isHalfHour && <span>{time}</span>}
    </div>
  );
}

