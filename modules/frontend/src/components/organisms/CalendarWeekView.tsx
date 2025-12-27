import { useState } from 'react';
import type { CalendarEvent } from '../../types/calendar';
import { startOfWeek, eachDayOfInterval, addDays } from 'date-fns';
import { WeekHeader } from './CalendarWeekView/WeekHeader';
import { TimeColumn } from './CalendarWeekView/TimeColumn';
import { DayColumn } from './CalendarWeekView/DayColumn';
import { normalizeDate, getDateString } from './CalendarWeekView/utils';

interface CalendarWeekViewProps {
  currentDate: Date;
  events: CalendarEvent[];
  selectedRoleId: string | null;
  onTimeSlotClick?: (date: Date, hour: number, minute: number) => void;
  onEventClick: (event: CalendarEvent) => void;
  onEventDragStart?: (event: CalendarEvent, e: React.DragEvent) => void;
  onEventDrop?: (eventId: string, date: Date, hour: number, minute: number) => void;
  onBusinessHoursClick?: (event: CalendarEvent) => void;
}

interface DragOverState {
  date: Date | null;
  hour: number | null;
  minute: number | null;
  event: CalendarEvent | null;
  eventId: string | null;
  dateString?: string;
}

export function CalendarWeekView({
  currentDate,
  events,
  selectedRoleId,
  onTimeSlotClick,
  onEventClick,
  onEventDragStart,
  onEventDrop,
  onBusinessHoursClick,
}: CalendarWeekViewProps) {
  const [dragOverState, setDragOverState] = useState<DragOverState>({
    date: null,
    hour: null,
    minute: null,
    event: null,
    eventId: null,
  });

  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const daysRaw = eachDayOfInterval({ start: weekStart, end: addDays(weekStart, 6) });
  const days = daysRaw.map(day => normalizeDate(day));

  const handleDragEnter = (date: Date, hour: number, minute: number) => {
    if (dragOverState.eventId) {
      const event = events.find(ev => ev.id === dragOverState.eventId);
      const normalizedDate = normalizeDate(date);
      const dateString = getDateString(normalizedDate);
      setDragOverState({ 
        ...dragOverState, 
        date: normalizedDate, 
        hour, 
        minute, 
        event: event || null,
        dateString
      });
    }
  };

  const handleDragLeave = () => {
    setDragOverState({ date: null, hour: null, minute: null, event: null, eventId: null, dateString: undefined });
  };

  const handleDrop = (e: React.DragEvent, date: Date, hour: number, minute: number) => {
    e.preventDefault();
    e.stopPropagation();
    const eventId = e.dataTransfer.getData('eventId') || dragOverState.eventId;
    if (eventId && onEventDrop) {
      if (dragOverState.date && dragOverState.hour !== null && dragOverState.minute !== null && dragOverState.dateString) {
        const [year, month, day] = dragOverState.dateString.split('-').map(Number);
        const dropDate = new Date(year, month - 1, day, 12, 0, 0);
        const finalDate = normalizeDate(dropDate);
        onEventDrop(eventId, finalDate, dragOverState.hour, dragOverState.minute);
      } else {
        const normalizedDate = normalizeDate(date);
        onEventDrop(eventId, normalizedDate, hour, minute);
      }
    }
    setDragOverState({ date: null, hour: null, minute: null, event: null, eventId: null, dateString: undefined });
  };

  return (
    <div className="flex-1 overflow-auto bg-white">
      <WeekHeader days={days} />

      <div className="flex relative">
        <TimeColumn />

        {days.map((day) => (
          <DayColumn
            key={day.toISOString()}
            date={day}
            events={events}
            selectedRoleId={selectedRoleId}
            dragOverState={dragOverState}
            onTimeSlotClick={onTimeSlotClick}
            onEventClick={onEventClick}
            onEventDragStart={onEventDragStart}
            onBusinessHoursClick={onBusinessHoursClick}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            setDragOverState={setDragOverState}
          />
        ))}
      </div>
    </div>
  );
}

