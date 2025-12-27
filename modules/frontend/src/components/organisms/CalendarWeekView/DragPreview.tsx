import type { CalendarEvent } from '../../../types/calendar';
import { normalizeDate, getDateString, SLOTS_PER_HOUR, TOTAL_SLOTS } from './utils';

interface DragPreviewProps {
  date: Date;
  dragOverState: {
    event: CalendarEvent | null;
    date: Date | null;
    hour: number | null;
    minute: number | null;
    dateString?: string;
  };
}

export function DragPreview({ date, dragOverState }: DragPreviewProps) {
  if (!dragOverState.date || !dragOverState.dateString) return null;

  const dayString = getDateString(date);
  if (dragOverState.dateString !== dayString) return null;

  if (!dragOverState.event || dragOverState.hour === null || dragOverState.minute === null) {
    return null;
  }

  const normalizedDragDate = normalizeDate(dragOverState.date);
  const normalizedDate = normalizeDate(date);
  const isSameDate = normalizedDragDate.getTime() === normalizedDate.getTime();

  if (!isSameDate) {
    return null;
  }

  const originalEvent = dragOverState.event;
  const previewHour = dragOverState.hour;
  const previewMinute = dragOverState.minute;

  const [originalStartHour, originalStartMinute] = originalEvent.start_time.split(':').map(Number);
  const [originalEndHour, originalEndMinute] = originalEvent.end_time.split(':').map(Number);
  const originalDuration = (originalEndHour * 60 + originalEndMinute) - (originalStartHour * 60 + originalStartMinute);
  const newEndMinutes = previewHour * 60 + previewMinute + originalDuration;
  const newEndHour = Math.floor(newEndMinutes / 60);
  const newEndMinute = newEndMinutes % 60;

  const startSlot = previewHour * SLOTS_PER_HOUR + (previewMinute >= 30 ? 1 : 0);
  const endSlot = newEndHour * SLOTS_PER_HOUR + (newEndMinute > 30 ? 1 : 0);
  const topPercent = (startSlot / TOTAL_SLOTS) * 100;
  const heightPercent = ((endSlot - startSlot) / TOTAL_SLOTS) * 100;

  return (
    <div
      className="absolute px-2 py-1 text-xs rounded border pointer-events-none"
      style={{
        top: `${topPercent}%`,
        left: '2.5px',
        width: 'calc(100% - 5px)',
        height: `${heightPercent}%`,
        minHeight: '20px',
        opacity: 0.6,
        border: '2px dashed #3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        zIndex: 20,
      }}
    >
      <div className="font-medium truncate">
        {originalEvent.type === 'availability' && originalEvent.person_name
          ? originalEvent.person_name
          : originalEvent.role_name}
      </div>
      <div className="text-xs opacity-75">
        {`${String(previewHour).padStart(2, '0')}:${String(previewMinute).padStart(2, '0')}`} - {`${String(newEndHour).padStart(2, '0')}:${String(newEndMinute).padStart(2, '0')}`}
      </div>
    </div>
  );
}

