import type { AvailabilityHours } from './availability';
import type { BusinessServiceHours } from './businessHours';

export type CalendarView = 'week' | 'month';
export type CalendarMode = 'planning' | 'schedule';

export interface CalendarEvent {
  id: string;
  type: 'availability' | 'business';
  person_id?: string;
  person_name?: string;
  role_id: string;
  role_name: string;
  date: Date;
  start_time: string;
  end_time: string;
  start_date?: Date;
  end_date?: Date;
  is_recurring: boolean;
  day_of_week?: number | null;
  specific_date?: Date | null;
}

export interface Person {
  id: string;
  name: string;
  email: string;
}

export interface Role {
  id: string;
  name: string;
  description: string | null;
}

export interface HoursFilters {
  role_id?: string | null;
  person_id?: string | null;
  start_date?: Date | null;
  end_date?: Date | null;
}

export function toCalendarEvent(
  item: AvailabilityHours | BusinessServiceHours,
  type: 'availability' | 'business',
  person?: Person,
  role?: Role
): CalendarEvent {
  return {
    id: item.id,
    type,
    person_id: 'person_id' in item ? item.person_id : undefined,
    person_name: person?.name,
    role_id: item.role_id,
    role_name: role?.name || '',
    date: item.specific_date ? new Date(item.specific_date) : new Date(),
    start_time: item.start_time,
    end_time: item.end_time,
    start_date: item.start_date ? new Date(item.start_date) : undefined,
    end_date: item.end_date ? new Date(item.end_date) : undefined,
    is_recurring: item.is_recurring,
    day_of_week: item.day_of_week,
    specific_date: item.specific_date ? new Date(item.specific_date) : undefined,
  };
}

