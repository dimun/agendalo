import { Input } from '../atoms/Input';
import { FormField } from './FormField';

interface TimeRangePickerProps {
  startTime: string;
  endTime: string;
  onStartTimeChange: (time: string) => void;
  onEndTimeChange: (time: string) => void;
  error?: { start?: string; end?: string };
}

export function TimeRangePicker({
  startTime,
  endTime,
  onStartTimeChange,
  onEndTimeChange,
  error,
}: TimeRangePickerProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <FormField label="Start Time" error={error?.start} required>
        <Input
          type="time"
          value={startTime}
          onChange={(e) => onStartTimeChange(e.target.value)}
          error={error?.start}
        />
      </FormField>
      <FormField label="End Time" error={error?.end} required>
        <Input
          type="time"
          value={endTime}
          onChange={(e) => onEndTimeChange(e.target.value)}
          error={error?.end}
        />
      </FormField>
    </div>
  );
}

