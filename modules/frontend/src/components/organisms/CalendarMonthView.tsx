import { CalendarEvent } from '../../types/calendar';
import { startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, format, isSameMonth, isSameDay, addDays } from 'date-fns';

interface CalendarMonthViewProps {
  currentDate: Date;
  events: CalendarEvent[];
  onDayClick: (date: Date) => void;
  onEventClick: (event: CalendarEvent) => void;
}

export function CalendarMonthView({
  currentDate,
  events,
  onDayClick,
  onEventClick,
}: CalendarMonthViewProps) {
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 });
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  const weekDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const weeks: Date[][] = [];
  for (let i = 0; i < days.length; i += 7) {
    weeks.push(days.slice(i, i + 7));
  }

  const getEventsForDay = (date: Date) => {
    return events.filter((event) => isSameDay(event.date, date));
  };

  return (
    <div className="flex-1 overflow-auto bg-white">
      <div className="grid grid-cols-7 border-b border-gray-200">
        {weekDays.map((day) => (
          <div key={day} className="text-center py-2 text-sm font-medium text-gray-700 border-r border-gray-200 last:border-r-0">
            {day}
          </div>
        ))}
      </div>

      {weeks.map((week, weekIndex) => (
        <div key={weekIndex} className="grid grid-cols-7 border-b border-gray-200">
          {week.map((day) => {
            const dayEvents = getEventsForDay(day);
            const isCurrentMonth = isSameMonth(day, currentDate);
            const isToday = isSameDay(day, new Date());

            return (
              <div
                key={day.toISOString()}
                className={`min-h-24 border-r border-gray-200 last:border-r-0 p-2 cursor-pointer hover:bg-gray-50 transition-colors ${
                  !isCurrentMonth ? 'bg-gray-50' : ''
                }`}
                onClick={() => onDayClick(day)}
              >
                <div
                  className={`text-sm mb-1 ${
                    isToday
                      ? 'bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center font-semibold'
                      : isCurrentMonth
                      ? 'text-gray-900'
                      : 'text-gray-400'
                  }`}
                >
                  {format(day, 'd')}
                </div>
                <div className="space-y-1">
                  {dayEvents.slice(0, 3).map((event) => (
                    <div
                      key={event.id}
                      onClick={(e) => {
                        e.stopPropagation();
                        onEventClick(event);
                      }}
                      className={`text-xs px-1 py-0.5 rounded truncate cursor-pointer ${
                        event.type === 'availability'
                          ? 'bg-blue-100 text-blue-900'
                          : 'bg-green-100 text-green-900'
                      }`}
                    >
                      {event.start_time} {event.type === 'availability' && event.person_name
                        ? event.person_name
                        : event.role_name}
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="text-xs text-gray-500">+{dayEvents.length - 3} more</div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}

