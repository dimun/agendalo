import { Input } from '../atoms/Input';
import { FormField } from './FormField';

interface DatePickerProps {
  label: string;
  value: string;
  onChange: (date: string) => void;
  error?: string;
  required?: boolean;
  min?: string;
  max?: string;
}

export function DatePicker({
  label,
  value,
  onChange,
  error,
  required,
  min,
  max,
}: DatePickerProps) {
  return (
    <FormField label={label} error={error} required={required}>
      <Input
        type="date"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        error={error}
        min={min}
        max={max}
      />
    </FormField>
  );
}

