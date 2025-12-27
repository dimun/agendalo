import type { CalendarEvent } from '../../../types/calendar';
import { TOTAL_SLOTS } from './utils';
import { getRoleColor } from '../../../utils/roleColors';

interface BusinessHoursBlockProps {
  event: CalendarEvent;
  startSlot: number;
  endSlot: number;
  onBusinessHoursClick?: (event: CalendarEvent) => void;
}

export function BusinessHoursBlock({
  event,
  startSlot,
  endSlot,
  onBusinessHoursClick,
}: BusinessHoursBlockProps) {
  const topPercent = (startSlot / TOTAL_SLOTS) * 100;
  const heightPercent = ((endSlot - startSlot) / TOTAL_SLOTS) * 100;
  const roleName = event.role_name || 'Business Hours';
  const roleColor = getRoleColor(event.role_id);

  const hexToRgba = (hex: string, alpha: number): string => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  return (
    <div
      className="absolute group"
      style={{
        top: `${topPercent}%`,
        left: 0,
        right: 0,
        height: `${heightPercent}%`,
        border: `4px solid ${roleColor.primary}`,
        borderRadius: '4px',
        boxSizing: 'border-box',
        backgroundColor: hexToRgba(roleColor.light, 0.3),
        zIndex: 5,
      }}
    >
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <span className="text-xs font-medium opacity-80 select-none" style={{ color: roleColor.text }}>
          {roleName} Business Hours
        </span>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          if (onBusinessHoursClick) {
            onBusinessHoursClick(event);
          }
        }}
        className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity bg-white-100/99 text-red-400 rounded p-1 shadow-md hover:scale-110 z-10"
        title="Delete business hours"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-4 w-4"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
          />
        </svg>
      </button>
    </div>
  );
}

