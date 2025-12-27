import { useState, useMemo } from 'react';
import type { CalendarView } from '../types/calendar';
import { startOfWeek, endOfWeek, addWeeks, subWeeks, startOfMonth, endOfMonth, addMonths, subMonths, format } from 'date-fns';

export function useCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<CalendarView>('week');

  const dateRange = useMemo(() => {
    if (view === 'week') {
      return {
        start: startOfWeek(currentDate, { weekStartsOn: 1 }),
        end: endOfWeek(currentDate, { weekStartsOn: 1 }),
      };
    } else {
      return {
        start: startOfMonth(currentDate),
        end: endOfMonth(currentDate),
      };
    }
  }, [currentDate, view]);

  const navigatePrevious = () => {
    if (view === 'week') {
      setCurrentDate(subWeeks(currentDate, 1));
    } else {
      setCurrentDate(subMonths(currentDate, 1));
    }
  };

  const navigateNext = () => {
    if (view === 'week') {
      setCurrentDate(addWeeks(currentDate, 1));
    } else {
      setCurrentDate(addMonths(currentDate, 1));
    }
  };

  const navigateToToday = () => {
    setCurrentDate(new Date());
  };

  const navigateToDate = (date: Date) => {
    setCurrentDate(date);
    if (view === 'month') {
      setView('week');
    }
  };

  const formattedDate = useMemo(() => {
    if (view === 'week') {
      const start = dateRange.start;
      const end = dateRange.end;
      if (format(start, 'MMM') === format(end, 'MMM')) {
        return `${format(start, 'MMM d')} - ${format(end, 'd, yyyy')}`;
      }
      return `${format(start, 'MMM d')} - ${format(end, 'MMM d, yyyy')}`;
    } else {
      return format(currentDate, 'MMMM yyyy');
    }
  }, [currentDate, view, dateRange]);

  return {
    currentDate,
    view,
    setView,
    dateRange,
    navigatePrevious,
    navigateNext,
    navigateToToday,
    navigateToDate,
    formattedDate,
  };
}

