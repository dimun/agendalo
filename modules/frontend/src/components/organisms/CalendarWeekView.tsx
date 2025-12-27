import type { CalendarEvent } from '../../types/calendar';
import { format, isSameDay, startOfWeek, eachDayOfInterval, addDays } from 'date-fns';
import { EventBlock } from './EventBlock';
import { TimeSlot } from '../atoms/TimeSlot';

interface CalendarWeekViewProps {
  currentDate: Date;
  events: CalendarEvent[];
  selectedRoleId: string | null;
  onTimeSlotClick: (date: Date, hour: number, minute: number) => void;
  onEventClick: (event: CalendarEvent) => void;
  onEventDragStart: (event: CalendarEvent, e: React.DragEvent) => void;
}

const HOURS = Array.from({ length: 24 }, (_, i) => i);
const SLOTS_PER_HOUR = 2;

export function CalendarWeekView({
  currentDate,
  events,
  selectedRoleId,
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

  const getBusinessHoursForSlot = (date: Date, slotIndex: number) => {
    const hour = Math.floor(slotIndex / SLOTS_PER_HOUR);
    const minute = (slotIndex % SLOTS_PER_HOUR) * 30;
    const slotTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:00`;
    
    return events.filter((event) => {
      if (event.type !== 'business') return false;
      if (!isSameDay(event.date, date)) return false;
      if (selectedRoleId && event.role_id !== selectedRoleId) return false;
      
      const [startHour, startMinute] = event.start_time.split(':').map(Number);
      const [endHour, endMinute] = event.end_time.split(':').map(Number);
      
      const eventStartMinutes = startHour * 60 + startMinute;
      const eventEndMinutes = endHour * 60 + endMinute;
      const slotMinutes = hour * 60 + minute;
      
      return slotMinutes >= eventStartMinutes && slotMinutes < eventEndMinutes;
    });
  };

  const getAvailabilityEventsForDay = (date: Date) => {
    return events.filter((event) => {
      if (event.type !== 'availability') return false;
      if (!isSameDay(event.date, date)) return false;
      if (selectedRoleId && event.role_id !== selectedRoleId) return false;
      return true;
    });
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
                const businessHours = getBusinessHoursForSlot(day, slotIndex);
                const hasBusinessHours = businessHours.length > 0;
                
                return (
                  <div
                    key={slotIndex}
                    className={`border-b border-gray-100 cursor-pointer transition-colors ${
                      hasBusinessHours
                        ? 'bg-green-50 hover:bg-green-100'
                        : 'hover:bg-blue-50'
                    }`}
                    style={{ height: `${100 / (24 * SLOTS_PER_HOUR)}%` }}
                    onClick={() => onTimeSlotClick(day, hour, minute)}
                  />
                );
              })}

              {layoutEvents(getAvailabilityEventsForDay(day)).map(({ event, style }) => {
                // Make availability events 5px smaller
                const adjustedStyle = {
                  ...style,
                  top: `calc(${style.top} + 2.5px)`,
                  left: `calc(${style.left} + 2.5px)`,
                  width: `calc(${style.width} - 5px)`,
                  height: `calc(${style.height} - 5px)`,
                  zIndex: 10, // Ensure availability is on top
                };
                
                return (
                  <EventBlock
                    key={event.id}
                    event={event}
                    onClick={() => onEventClick(event)}
                    onDragStart={(e) => onEventDragStart(event, e)}
                    style={adjustedStyle}
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

