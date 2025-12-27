import { useState } from 'react';
import type { Role } from '../../types/calendar';
import type { BusinessServiceHoursBulkCreate } from '../../types/businessHours';
import { Button } from '../atoms/Button';
import { Select } from '../atoms/Select';
import { FormField } from '../molecules/FormField';
import { TimeRangePicker } from '../molecules/TimeRangePicker';
import { DatePicker } from '../molecules/DatePicker';

interface BusinessHoursBulkFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: BusinessServiceHoursBulkCreate) => Promise<void>;
  roles: Role[];
}

export function BusinessHoursBulkFormModal({
  isOpen,
  onClose,
  onSubmit,
  roles,
}: BusinessHoursBulkFormModalProps) {
  const [roleId, setRoleId] = useState('');
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('17:00');
  const [days, setDays] = useState('mon-fri');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data: BusinessServiceHoursBulkCreate = {
        role_id: roleId,
        start_time: startTime,
        end_time: endTime,
        days: days,
        start_date: startDate || null,
        end_date: endDate || null,
      };
      await onSubmit(data);
      onClose();
      setRoleId('');
      setStartTime('09:00');
      setEndTime('17:00');
      setDays('mon-fri');
      setStartDate('');
      setEndDate('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-semibold mb-4">Add Business Hours (Bulk)</h2>

        <form onSubmit={handleSubmit}>
          <FormField label="Role" required>
            <Select value={roleId} onChange={(e) => setRoleId(e.target.value)} required>
              <option value="">Select a role</option>
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </Select>
          </FormField>

          <TimeRangePicker
            startTime={startTime}
            endTime={endTime}
            onStartTimeChange={setStartTime}
            onEndTimeChange={setEndTime}
          />

          <FormField label="Days" required>
            <Select value={days} onChange={(e) => setDays(e.target.value)} required>
              <option value="mon-fri">Monday - Friday</option>
              <option value="mon-sat">Monday - Saturday</option>
              <option value="all">All Days (Monday - Sunday)</option>
            </Select>
          </FormField>

          <DatePicker
            label="Start Date (optional)"
            value={startDate}
            onChange={setStartDate}
          />

          <DatePicker
            label="End Date (optional)"
            value={endDate}
            onChange={setEndDate}
            min={startDate}
          />

          {error && <div className="text-red-600 text-sm mb-4">{error}</div>}

          <div className="flex justify-end gap-2 mt-6">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

