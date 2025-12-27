import { format } from 'date-fns';

interface WeekHeaderProps {
  days: Date[];
}

export function WeekHeader({ days }: WeekHeaderProps) {
  return (
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
  );
}

