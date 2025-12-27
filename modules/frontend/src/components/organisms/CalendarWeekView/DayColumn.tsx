import type { CalendarEvent } from '../../../types/calendar';
import { EventBlock } from '../EventBlock';
import { SLOTS_PER_HOUR, TOTAL_SLOTS, getBusinessHoursBlocks, getAvailabilityEventsForDay, layoutEvents } from './utils';
import { BusinessHoursBlock } from './BusinessHoursBlock';
import { TimeSlotCell } from './TimeSlotCell';
import { DragPreview } from './DragPreview';

interface DayColumnProps {
  date: Date;
  events: CalendarEvent[];
  selectedRoleId: string | null;
  dragOverState: {
    date: Date | null;
    hour: number | null;
    minute: number | null;
    event: CalendarEvent | null;
    eventId: string | null;
    dateString?: string;
  };
  onTimeSlotClick: (date: Date, hour: number, minute: number) => void;
  onEventClick: (event: CalendarEvent) => void;
  onEventDragStart: (event: CalendarEvent, e: React.DragEvent) => void;
  onBusinessHoursClick?: (event: CalendarEvent) => void;
  onDragEnter: (date: Date, hour: number, minute: number) => void;
  onDragLeave: () => void;
  onDrop: (e: React.DragEvent, date: Date, hour: number, minute: number) => void;
  setDragOverState: (state: {
    date: Date | null;
    hour: number | null;
    minute: number | null;
    event: CalendarEvent | null;
    eventId: string | null;
    dateString?: string;
  }) => void;
}

export function DayColumn({
  date,
  events,
  selectedRoleId,
  dragOverState,
  onTimeSlotClick,
  onEventClick,
  onEventDragStart,
  onBusinessHoursClick,
  onDragEnter,
  onDragLeave,
  onDrop,
  setDragOverState,
}: DayColumnProps) {
  const businessBlocks = getBusinessHoursBlocks(events, date, selectedRoleId);
  const availabilityEvents = getAvailabilityEventsForDay(events, date, selectedRoleId);

  return (
    <div className="flex-1 border-r border-gray-200 relative">
      <div className="relative" style={{ height: `${24 * 48}px` }}>
        {Array.from({ length: TOTAL_SLOTS }).map((_, slotIndex) => {
          const hour = Math.floor(slotIndex / SLOTS_PER_HOUR);
          const minute = (slotIndex % SLOTS_PER_HOUR) * 30;

          return (
            <TimeSlotCell
              key={slotIndex}
              date={date}
              slotIndex={slotIndex}
              hour={hour}
              minute={minute}
              events={events}
              selectedRoleId={selectedRoleId}
              dragOverState={dragOverState}
              onTimeSlotClick={onTimeSlotClick}
              onDragEnter={onDragEnter}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            />
          );
        })}

        {businessBlocks.map((block, blockIndex) => (
          <BusinessHoursBlock
            key={`block-${blockIndex}`}
            event={block.event}
            startSlot={block.startSlot}
            endSlot={block.endSlot}
            onBusinessHoursClick={onBusinessHoursClick}
          />
        ))}

        {layoutEvents(availabilityEvents).map(({ event, style }) => {
          const adjustedStyle = {
            ...style,
            top: `calc(${style.top} + 2.5px)`,
            left: `calc(${style.left} + 2.5px)`,
            width: `calc(${style.width} - 5px)`,
            height: `calc(${style.height} - 5px)`,
            zIndex: 10,
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

        <DragPreview date={date} dragOverState={dragOverState} />
      </div>
    </div>
  );
}

