import type { CalendarEvent } from '../../types/calendar';
import { format, isSameDay, startOfWeek, eachDayOfInterval, addDays } from 'date-fns';
import { EventBlock } from './EventBlock';
import { TimeSlot } from '../atoms/TimeSlot';

interface CalendarWeekViewProps {
  currentDate: Date;
  events: CalendarEvent[];
  onTimeSlotClick: (date: Date, hour: number, minute: number) => void;
  onEventClick: (event: CalendarEvent) => void;
  onEventDragStart: (event: CalendarEvent, e: React.DragEvent) => void;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const SLOTS_PER_HOUR = 2;

export function CalendarWeekView({
  currentDate,
  events,
  onTimeSlotClick,
  onEventClick,
  onEventDragStart,
}: CalendarWeekViewProps) {
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const days = eachDayOfInterval({ start: weekStart, end: addDays(weekStart, 6) });

  const getEventPosition = (event: CalendarEvent) => {
    const [startHour, startMinute] = event.start_time.split(':').map(Number);
    const [endHour, endMinute] = event.end_time.split(':').map(Number);
    
    const startSlot = startHour * SLOTS_PER_HOUR + (startMinute >= 30 ? 1 : 0);
    const endSlot = endHour * SLOTS_PER_HOUR + (endMinute > 30 ? 1 : 0);
    const duration = endSlot - startSlot;
    
    const topPercent = (startSlot / (24 * SLOTS_PER_HOUR)) * 100;
    const heightPercent = (duration / (24 * SLOTS_PER_HOUR)) * 100;
    
    return {
      top: `${topPercent}%`,
      height: `${heightPercent}%`,
    };
  };

  const getEventsForDay = (date: Date) => {
    return events.filter((event) => isSameDay(event.date, date));
  };

  return (
    <div className="flex-1 overflow-auto bg-white">
      <div className="flex border-b border-gray-200">
        <div className="w-16 border-r border-gray-200"></div>
        {days.map((day) => (
          <div key={day.toISOString()} className="flex-1 border-r border-gray-200">
            <div className="text-center py-2 border-b border-gray-200">
              <div className="text-xs text-gray-500">{format(day, 'EEE')}</div>
              <div className="text-lg font-semibold">{format(day, 'd')}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="flex relative">
        <div className="w-16 border-r border-gray-200">
          {HOURS.map((hour) => (
            <TimeSlot key={hour} time={`${String(hour).padStart(2, '0')}:00`} />
          ))}
        </div>

        {days.map((day) => (
          <div key={day.toISOString()} className="flex-1 border-r border-gray-200 relative">
            <div className="relative" style={{ height: `${24 * 48}px` }}>
              {Array.from({ length: 24 * SLOTS_PER_HOUR }).map((_, slotIndex) => {
                const hour = Math.floor(slotIndex / SLOTS_PER_HOUR);
                const minute = (slotIndex % SLOTS_PER_HOUR) * 30;
                return (
                  <div
                    key={slotIndex}
                    className="border-b border-gray-100 cursor-pointer hover:bg-blue-50 transition-colors"
                    style={{ height: `${100 / (24 * SLOTS_PER_HOUR)}%` }}
                    onClick={() => onTimeSlotClick(day, hour, minute)}
                  />
                );
              })}

              {getEventsForDay(day).map((event) => {
                const position = getEventPosition(event);
                return (
                  <EventBlock
                    key={event.id}
                    event={event}
                    onClick={() => onEventClick(event)}
                    onDragStart={(e) => onEventDragStart(event, e)}
                    style={{
                      ...position,
                      minHeight: '20px',
                    }}
                  />
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

