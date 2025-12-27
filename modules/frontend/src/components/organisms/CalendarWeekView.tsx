import { useState } from 'react';
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
  onEventDrop?: (eventId: string, date: Date, hour: number, minute: number) => void;
  onBusinessHoursClick?: (event: CalendarEvent) => void;
}

interface DragOverState {
  date: Date | null;
  hour: number | null;
  minute: number | null;
  event: CalendarEvent | null;
  eventId: string | null;
  dateString?: string; // ISO date string for easier comparison
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

  const normalizeDate = (date: Date): Date => {
    // Use local date components to avoid timezone issues
    const normalized = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    return normalized;
  };

  const getDateString = (date: Date): string => {
    // Get date string in local timezone (YYYY-MM-DD)
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const daysRaw = eachDayOfInterval({ start: weekStart, end: addDays(weekStart, 6) });
  // Normalize all days to midnight to avoid timezone issues
  const days = daysRaw.map(day => normalizeDate(day));

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

  const getBusinessHoursForSlot = (date: Date, slotIndex: number) => {
    const hour = Math.floor(slotIndex / SLOTS_PER_HOUR);
    const minute = (slotIndex % SLOTS_PER_HOUR) * 30;
    
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

  const getBusinessHoursBlocks = (date: Date) => {
    const businessEvents = events.filter((event) => {
      if (event.type !== 'business') return false;
      if (!isSameDay(event.date, date)) return false;
      if (selectedRoleId && event.role_id !== selectedRoleId) return false;
      return true;
    });

    return businessEvents.map((event) => {
      const [startHour, startMinute] = event.start_time.split(':').map(Number);
      const [endHour, endMinute] = event.end_time.split(':').map(Number);
      
      const startSlot = startHour * SLOTS_PER_HOUR + (startMinute >= 30 ? 1 : 0);
      const endSlot = endHour * SLOTS_PER_HOUR + (endMinute > 30 ? 1 : 0);
      
      return { event, startSlot, endSlot };
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

  const handleDragEnter = (date: Date, hour: number, minute: number) => {
    if (dragOverState.eventId) {
      const event = events.find(ev => ev.id === dragOverState.eventId);
      const normalizedDate = normalizeDate(date);
      // Store the date string in local timezone (YYYY-MM-DD)
      const dateString = getDateString(normalizedDate);
      setDragOverState({ 
        ...dragOverState, 
        date: normalizedDate, 
        hour, 
        minute, 
        event: event || null,
        dateString // Store for comparison
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
      // Always use dragOverState values if available - these are what the preview is showing
      if (dragOverState.date && dragOverState.hour !== null && dragOverState.minute !== null && dragOverState.dateString) {
        // Reconstruct the date from the dateString to ensure we use the correct local date
        // Use the dateString directly to create a date in local timezone
        const [year, month, day] = dragOverState.dateString.split('-').map(Number);
        // Create date using local timezone (year, month-1, day) - this creates midnight local time
        const dropDate = new Date(year, month - 1, day, 12, 0, 0); // Use noon to avoid timezone edge cases
        
        // Use the date from dragOverState which is already normalized to local midnight
        const finalDate = normalizeDate(dropDate);
        onEventDrop(eventId, finalDate, dragOverState.hour, dragOverState.minute);
      } else {
        // Fallback to parameters if dragOverState is not available
        const normalizedDate = normalizeDate(date);
        onEventDrop(eventId, normalizedDate, hour, minute);
      }
    }
    setDragOverState({ date: null, hour: null, minute: null, event: null, eventId: null, dateString: undefined });
  };

  const getPreviewEvent = (date: Date) => {
    if (!dragOverState.event || !dragOverState.date || 
        dragOverState.hour === null || dragOverState.minute === null) {
      return null;
    }
    
    // Normalize both dates to midnight for accurate comparison
    const normalizedDragDate = normalizeDate(dragOverState.date);
    const normalizedDate = normalizeDate(date);
    
    // Compare dates more carefully - check if they're the same day
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
    const topPercent = (startSlot / (24 * SLOTS_PER_HOUR)) * 100;
    const heightPercent = ((endSlot - startSlot) / (24 * SLOTS_PER_HOUR)) * 100;

    return {
      event: originalEvent,
      startTime: `${String(previewHour).padStart(2, '0')}:${String(previewMinute).padStart(2, '0')}`,
      endTime: `${String(newEndHour).padStart(2, '0')}:${String(newEndMinute).padStart(2, '0')}`,
      style: {
        top: `${topPercent}%`,
        left: '2.5px',
        width: 'calc(100% - 5px)',
        height: `${heightPercent}%`,
        minHeight: '20px',
        opacity: 0.6,
        border: '2px dashed #3b82f6',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        zIndex: 20,
      },
    };
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

        {days.map((day) => {
          const businessBlocks = getBusinessHoursBlocks(day);
          
          return (
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
                      style={{ height: `${100 / (24 * SLOTS_PER_HOUR)}%` }}
                      onClick={() => onTimeSlotClick(day, hour, minute)}
                      onDragOver={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        e.dataTransfer.dropEffect = 'move';
                        // Normalize the day to ensure consistent comparison
                        const normalizedDay = normalizeDate(day);
                        handleDragEnter(normalizedDay, hour, minute);
                      }}
                      onDragLeave={(e) => {
                        // Only clear if we're leaving the time slot (not entering a child)
                        const rect = (e.currentTarget as HTMLElement).getBoundingClientRect();
                        const x = e.clientX;
                        const y = e.clientY;
                        if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
                          handleDragLeave();
                        }
                      }}
                      onDrop={(e) => handleDrop(e, day, hour, minute)}
                      className={`border-b cursor-pointer transition-colors relative ${
                        hasBusinessHours
                          ? 'bg-green-50 hover:bg-green-100'
                          : 'border-gray-100 hover:bg-blue-50'
                      } ${
                        (() => {
                          if (!dragOverState.date || !dragOverState.dateString || dragOverState.hour === null || dragOverState.minute === null) {
                            return false;
                          }
                          // Compare using date strings to avoid timezone issues
                          const dayString = getDateString(day);
                          const isSameDate = dragOverState.dateString === dayString;
                          return isSameDate && dragOverState.hour === hour && dragOverState.minute === minute;
                        })()
                          ? 'bg-blue-200 border-blue-400 border-2'
                          : ''
                      }`}
                    >
                    </div>
                  );
                })}

                {/* Render clickable business hours blocks */}
                {businessBlocks.map((block, blockIndex) => {
                  const topPercent = (block.startSlot / (24 * SLOTS_PER_HOUR)) * 100;
                  const heightPercent = ((block.endSlot - block.startSlot) / (24 * SLOTS_PER_HOUR)) * 100;
                  const roleName = block.event.role_name || 'Business Hours';
                  
                  return (
                    <div
                      key={`block-${blockIndex}`}
                      className="absolute group"
                      style={{
                        top: `${topPercent}%`,
                        left: 0,
                        right: 0,
                        height: `${heightPercent}%`,
                        border: '4px solid #4ade80', // green-400
                        borderRadius: '4px',
                        boxSizing: 'border-box',
                        zIndex: 5,
                      }}
                    >
                      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                        <span className="text-xs text-green-700 font-medium opacity-40 select-none">
                          {roleName} Business Hours
                        </span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onBusinessHoursClick) {
                            onBusinessHoursClick(block.event);
                          }
                        }}
                        className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 hover:bg-red-600 text-white rounded p-1 shadow-md z-10"
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
                             onDragStart={(e) => {
                               onEventDragStart(event, e);
                               setDragOverState({ date: null, hour: null, minute: null, event: event, eventId: event.id });
                             }}
                             style={adjustedStyle}
                           />
                         );
                       })}

                {/* Preview of dragged event - only render in the correct day column */}
                {(() => {
                  // Only render preview if this is the correct day column
                  if (!dragOverState.date || !dragOverState.dateString) return null;
                  
                  // Compare using local date strings to avoid timezone issues
                  const dayString = getDateString(day);
                  if (dragOverState.dateString !== dayString) return null;
                  
                  const preview = getPreviewEvent(day);
                  if (!preview) return null;
                  return (
                    <div
                      className="absolute px-2 py-1 text-xs rounded border pointer-events-none"
                      style={preview.style}
                    >
                      <div className="font-medium truncate">
                        {preview.event.type === 'availability' && preview.event.person_name
                          ? preview.event.person_name
                          : preview.event.role_name}
                      </div>
                      <div className="text-xs opacity-75">
                        {preview.startTime} - {preview.endTime}
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

