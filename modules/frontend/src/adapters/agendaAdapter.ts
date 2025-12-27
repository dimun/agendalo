import type { AgendaEntry } from '../types/agenda';
import type { CalendarEvent } from '../types/calendar';
import type { Person, Role } from '../types/calendar';

export function agendaEntriesToCalendarEvents(
  entries: AgendaEntry[],
  people: Person[],
  roles: Role[]
): CalendarEvent[] {
  return entries.map((entry) => {
    const person = people.find((p) => p.id === entry.person_id);
    const role = roles.find((r) => r.id === entry.role_id);
    
    const dateString = entry.date;
    const [year, month, day] = dateString.split('T')[0].split('-').map(Number);
    const date = new Date(year, month - 1, day);
    
    return {
      id: entry.id,
      type: 'schedule',
      person_id: entry.person_id,
      person_name: person?.name,
      role_id: entry.role_id,
      role_name: role?.name || '',
      date: date,
      start_time: entry.start_time,
      end_time: entry.end_time,
      is_recurring: false,
      specific_date: date,
    };
  });
}

