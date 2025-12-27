import { SLOTS_PER_HOUR, TOTAL_SLOTS, normalizeDate, getDateString, getBusinessHoursForSlot } from './utils';
import type { CalendarEvent } from '../../../types/calendar';

interface TimeSlotCellProps {
  date: Date;
  slotIndex: number;
  hour: number;
  minute: number;
  events: CalendarEvent[];
  selectedRoleId: string | null;
  dragOverState: {
    date: Date | null;
    hour: number | null;
    minute: number | null;
    dateString?: string;
  };
  onTimeSlotClick?: (date: Date, hour: number, minute: number) => void;
  onDragEnter?: (date: Date, hour: number, minute: number) => void;
  onDragLeave?: () => void;
  onDrop?: (e: React.DragEvent, date: Date, hour: number, minute: number) => void;
}

export function TimeSlotCell({
  date,
  slotIndex,
  hour,
  minute,
  events,
  selectedRoleId,
  dragOverState,
  onTimeSlotClick,
  onDragEnter,
  onDragLeave,
  onDrop,
}: TimeSlotCellProps) {
  const businessHours = getBusinessHoursForSlot(events, date, slotIndex, selectedRoleId);
  const hasBusinessHours = businessHours.length > 0;

  const isDragOver = (() => {
    if (!dragOverState.date || !dragOverState.dateString || dragOverState.hour === null || dragOverState.minute === null) {
      return false;
    }
    const dayString = getDateString(date);
    const isSameDate = dragOverState.dateString === dayString;
    return isSameDate && dragOverState.hour === hour && dragOverState.minute === minute;
  })();

  return (
    <div
      style={{ height: `${100 / TOTAL_SLOTS}%` }}
      onClick={onTimeSlotClick ? () => onTimeSlotClick(date, hour, minute) : undefined}
      onDragOver={onDragEnter ? (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.dataTransfer.dropEffect = 'move';
        const normalizedDay = normalizeDate(date);
        onDragEnter(normalizedDay, hour, minute);
      } : undefined}
      onDragLeave={onDragLeave ? (e) => {
        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
        const x = e.clientX;
        const y = e.clientY;
        if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
          onDragLeave();
        }
      } : undefined}
      onDrop={onDrop ? (e) => onDrop(e, date, hour, minute) : undefined}
      className={`border-b transition-colors relative ${
        onTimeSlotClick ? 'cursor-pointer' : ''
      } ${
        hasBusinessHours
          ? 'bg-green-50 hover:bg-green-100'
          : 'border-gray-100 hover:bg-blue-50'
      } ${
        isDragOver
          ? 'bg-blue-200 border-blue-400 border-2'
          : ''
      }`}
    >
    </div>
  );
}

