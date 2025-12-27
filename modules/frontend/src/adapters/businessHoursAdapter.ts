import type { BusinessServiceHours } from '../types/businessHours';
import type { CalendarEvent } from '../types/calendar';
import { startOfWeek, endOfWeek, eachDayOfInterval, format, parseISO } from 'date-fns';

export function expandBusinessServiceHours(
  hours: BusinessServiceHours,
  startDate: Date,
  endDate: Date
): CalendarEvent[] {
  const events: CalendarEvent[] = [];
  const weekStart = startOfWeek(startDate, { weekStartsOn: 1 });
  const weekEnd = endOfWeek(endDate, { weekStartsOn: 1 });
  const dateRange = eachDayOfInterval({ start: weekStart, end: weekEnd });

  if (hours.specific_date) {
    const specificDate = parseISO(hours.specific_date);
    if (specificDate >= startDate && specificDate <= endDate) {
      events.push({
        id: hours.id,
        type: 'business',
        role_id: hours.role_id,
        role_name: '',
        date: specificDate,
        start_time: hours.start_time,
        end_time: hours.end_time,
        is_recurring: false,
        specific_date: specificDate,
      });
    }
  } else if (hours.is_recurring && hours.day_of_week !== null) {
    dateRange.forEach((date) => {
      if (date.getDay() === hours.day_of_week) {
        const start = hours.start_date ? parseISO(hours.start_date) : null;
        const end = hours.end_date ? parseISO(hours.end_date) : null;

        if ((!start || date >= start) && (!end || date <= end)) {
          events.push({
            id: `${hours.id}-${format(date, 'yyyy-MM-dd')}`,
            type: 'business',
            role_id: hours.role_id,
            role_name: '',
            date: date,
            start_time: hours.start_time,
            end_time: hours.end_time,
            is_recurring: true,
            day_of_week: hours.day_of_week,
          });
        }
      }
    });
  } else if (hours.start_date && hours.end_date) {
    const start = parseISO(hours.start_date);
    const end = parseISO(hours.end_date);
    const range = eachDayOfInterval({ start, end });

    range.forEach((date) => {
      if (date >= startDate && date <= endDate) {
        events.push({
          id: `${hours.id}-${format(date, 'yyyy-MM-dd')}`,
          type: 'business',
          role_id: hours.role_id,
          role_name: '',
          date: date,
          start_time: hours.start_time,
          end_time: hours.end_time,
          is_recurring: false,
          start_date: start,
          end_date: end,
        });
      }
    });
  }

  return events;
}

export function toCalendarEvents(
  hoursList: BusinessServiceHours[],
  startDate: Date,
  endDate: Date
): CalendarEvent[] {
  const allEvents: CalendarEvent[] = [];

  hoursList.forEach((hours) => {
    const events = expandBusinessServiceHours(hours, startDate, endDate);
    allEvents.push(...events);
  });

  return allEvents;
}

