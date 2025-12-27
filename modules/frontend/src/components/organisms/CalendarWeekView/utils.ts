import type { CalendarEvent } from '../../../types/calendar';
import { isSameDay } from 'date-fns';

export const SLOTS_PER_HOUR = 2;
export const TOTAL_SLOTS = 24 * SLOTS_PER_HOUR;

export const normalizeDate = (date: Date): Date => {
  const normalized = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  return normalized;
};

export const getDateString = (date: Date): string => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

export const getEventSlotRange = (event: CalendarEvent) => {
  const [startHour, startMinute] = event.start_time.split(':').map(Number);
  const [endHour, endMinute] = event.end_time.split(':').map(Number);
  
  const startSlot = startHour * SLOTS_PER_HOUR + (startMinute >= 30 ? 1 : 0);
  const endSlot = endHour * SLOTS_PER_HOUR + (endMinute > 30 ? 1 : 0);
  
  return { startSlot, endSlot };
};

export const eventsOverlap = (event1: CalendarEvent, event2: CalendarEvent) => {
  const range1 = getEventSlotRange(event1);
  const range2 = getEventSlotRange(event2);
  
  return !(range1.endSlot <= range2.startSlot || range2.endSlot <= range1.startSlot);
};

export const layoutEvents = (dayEvents: CalendarEvent[]) => {
  const columns: CalendarEvent[][] = [];
  
  dayEvents.forEach((event) => {
    let placed = false;
    
    for (const column of columns) {
      const overlaps = column.some((e) => eventsOverlap(e, event));
      if (!overlaps) {
        column.push(event);
        placed = true;
        break;
      }
    }
    
    if (!placed) {
      columns.push([event]);
    }
  });
  
  const margin = 1;
  return dayEvents.map((event) => {
    const columnIndex = columns.findIndex((col) => col.includes(event));
    const columnWidth = (100 - (columns.length - 1) * margin) / columns.length;
    const left = columnIndex * (columnWidth + margin);
    
    const { startSlot, endSlot } = getEventSlotRange(event);
    const topPercent = (startSlot / TOTAL_SLOTS) * 100;
    const heightPercent = ((endSlot - startSlot) / TOTAL_SLOTS) * 100;
    
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

export const getBusinessHoursForSlot = (
  events: CalendarEvent[],
  date: Date,
  slotIndex: number,
  selectedRoleId: string | null
) => {
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

export const getBusinessHoursBlocks = (
  events: CalendarEvent[],
  date: Date,
  selectedRoleId: string | null
) => {
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

export const getAvailabilityEventsForDay = (
  events: CalendarEvent[],
  date: Date,
  selectedRoleId: string | null
) => {
  return events.filter((event) => {
    if (event.type !== 'availability') return false;
    if (!isSameDay(event.date, date)) return false;
    if (selectedRoleId && event.role_id !== selectedRoleId) return false;
    return true;
  });
};

export const getScheduleEventsForDay = (
  events: CalendarEvent[],
  date: Date,
  selectedRoleId: string | null
) => {
  const normalizedDate = normalizeDate(date);
  return events.filter((event) => {
    if (event.type !== 'schedule') return false;
    const normalizedEventDate = normalizeDate(event.date);
    if (!isSameDay(normalizedEventDate, normalizedDate)) return false;
    if (selectedRoleId && event.role_id !== selectedRoleId) return false;
    return true;
  });
};

