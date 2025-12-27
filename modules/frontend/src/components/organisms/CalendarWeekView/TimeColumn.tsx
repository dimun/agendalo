import { TimeSlot } from '../../atoms/TimeSlot';

const HOURS = Array.from({ length: 24 }, (_, i) => i);

export function TimeColumn() {
  return (
    <div className="w-16 border-r border-gray-200">
      {HOURS.map((hour) => (
        <TimeSlot key={hour} time={`${String(hour).padStart(2, '0')}:00`} />
      ))}
    </div>
  );
}

