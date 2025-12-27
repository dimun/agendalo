import type { CalendarEvent } from '../../types/calendar';

interface EventBlockProps {
  event: CalendarEvent;
  onClick?: () => void;
  onDragStart?: (e: React.DragEvent) => void;
  style?: React.CSSProperties;
}

export function EventBlock({ event, onClick, onDragStart, style }: EventBlockProps) {
  const bgColor =
    event.type === 'availability'
      ? 'bg-blue-100 border-blue-300 text-blue-900'
      : 'bg-green-100 border-green-300 text-green-900';

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onClick={onClick}
      className={`absolute left-0 right-0 px-2 py-1 text-xs rounded border cursor-move hover:opacity-80 transition-opacity ${bgColor}`}
      style={style}
    >
      <div className="font-medium truncate">
        {event.type === 'availability' && event.person_name
          ? event.person_name
          : event.role_name}
      </div>
      <div className="text-xs opacity-75">
        {event.start_time} - {event.end_time}
      </div>
    </div>
  );
}

