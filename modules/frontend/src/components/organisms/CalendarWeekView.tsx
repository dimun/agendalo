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

  const getEventSlotRange = (event: CalendarEvent) => {
    const [startHour, startMinute] = event.start_time.split(':').map(Number);
    const [endHour, endMinute] = event.end_time.split(':').map(Number);
    
    const startSlot = startHour * SLOTS_PER_HOUR + (startMinute >= 30 ? 1 : 0);
    const endSlot = endHour * SLOTS_PER_HOUR + (endMinute > 30 ? 1 : 0);
    
    return { startSlot, endSlot };
  };

  const eventsOverlap = (event1: CalendarEvent, event2: CalendarEvent) => {
    const range1 = getEventSlotRange(event1);
    const range2 = getEventSlotRange(event2);
    
    return !(range1.endSlot <= range2.startSlot || range2.endSlot <= range1.startSlot);
  };

  const layoutEvents = (dayEvents: CalendarEvent[]) => {
    // Group overlapping events into columns
    const columns: CalendarEvent[][] = [];
    
    dayEvents.forEach((event) => {
      let placed = false;
      
      // Try to place event in existing column
      for (const column of columns) {
        const overlaps = column.some((e) => eventsOverlap(e, event));
        if (!overlaps) {
          column.push(event);
          placed = true;
          break;
        }
      }
      
      // If no column available, create new one
      if (!placed) {
        columns.push([event]);
      }
    });
    
    // Assign position to each event
    const margin = 1; // 1% margin between events
    return dayEvents.map((event) => {
      const columnIndex = columns.findIndex((col) => col.includes(event));
      const columnWidth = (100 - (columns.length - 1) * margin) / columns.length;
      const left = columnIndex * (columnWidth + margin);
      
      const { startSlot, endSlot } = getEventSlotRange(event);
      const topPercent = (startSlot / (24 * SLOTS_PER_HOUR)) * 100;
      const heightPercent = ((endSlot - startSlot) / (24 * SLOTS_PER_HOUR)) * 100;
      
      return {
        event,
        style: {
          top: `${topPercent}%`,
          left: `${left}%`,
          width: `${columnWidth}%`,
          height: `${heightPercent}%`,
          minHeight: '20px',
        },
      };
    });
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

              {layoutEvents(getEventsForDay(day)).map(({ event, style }) => (
                <EventBlock
                  key={event.id}
                  event={event}
                  onClick={() => onEventClick(event)}
                  onDragStart={(e) => onEventDragStart(event, e)}
                  style={style}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

