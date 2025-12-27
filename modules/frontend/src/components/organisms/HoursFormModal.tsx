import { useState, useEffect } from 'react';
import { Person, Role } from '../../types/calendar';
import { AvailabilityHoursCreate } from '../../types/availability';
import { BusinessServiceHoursCreate } from '../../types/businessHours';
import { Button } from '../atoms/Button';
import { Select } from '../atoms/Select';
import { FormField } from '../molecules/FormField';
import { TimeRangePicker } from '../molecules/TimeRangePicker';
import { DatePicker } from '../molecules/DatePicker';

interface HoursFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: AvailabilityHoursCreate | BusinessServiceHoursCreate, personId?: string) => Promise<void>;
  type: 'availability' | 'business';
  people: Person[];
  roles: Role[];
  initialDate?: Date;
  initialTime?: { start: string; end: string };
}

export function HoursFormModal({
  isOpen,
  onClose,
  onSubmit,
  type,
  people,
  roles,
  initialDate,
  initialTime,
}: HoursFormModalProps) {
  const [roleId, setRoleId] = useState('');
  const [personId, setPersonId] = useState('');
  const [startTime, setStartTime] = useState(initialTime?.start || '09:00');
  const [endTime, setEndTime] = useState(initialTime?.end || '17:00');
  const [isRecurring, setIsRecurring] = useState(true);
  const [dayOfWeek, setDayOfWeek] = useState<number | null>(null);
  const [specificDate, setSpecificDate] = useState(
    initialDate ? initialDate.toISOString().split('T')[0] : ''
  );
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialDate) {
      setSpecificDate(initialDate.toISOString().split('T')[0]);
      setIsRecurring(false);
    }
  }, [initialDate]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (type === 'availability') {
        if (!personId) {
          setError('Person is required');
          setLoading(false);
          return;
        }
        const data: AvailabilityHoursCreate = {
          role_id: roleId,
          start_time: startTime,
          end_time: endTime,
          is_recurring: isRecurring,
          day_of_week: isRecurring ? dayOfWeek : null,
          specific_date: isRecurring ? null : specificDate || null,
          start_date: isRecurring && startDate ? startDate : null,
          end_date: isRecurring && endDate ? endDate : null,
        };
        await onSubmit(data, personId);
      } else {
        const data: BusinessServiceHoursCreate = {
          role_id: roleId,
          start_time: startTime,
          end_time: endTime,
          is_recurring: isRecurring,
          day_of_week: isRecurring ? dayOfWeek : null,
          specific_date: isRecurring ? null : specificDate || null,
          start_date: isRecurring && startDate ? startDate : null,
          end_date: isRecurring && endDate ? endDate : null,
        };
        await onSubmit(data);
      }
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
        <h2 className="text-xl font-semibold mb-4">
          Add {type === 'availability' ? 'Availability' : 'Business Service'} Hours
        </h2>

        <form onSubmit={handleSubmit}>
          {type === 'availability' && (
            <FormField label="Person" required>
              <Select
                value={personId}
                onChange={(e) => setPersonId(e.target.value)}
                required
              >
                <option value="">Select a person</option>
                {people.map((person) => (
                  <option key={person.id} value={person.id}>
                    {person.name}
                  </option>
                ))}
              </Select>
            </FormField>
          )}

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

          <FormField label="Type">
            <div className="flex gap-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={isRecurring}
                  onChange={() => setIsRecurring(true)}
                  className="mr-2"
                />
                Recurring
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  checked={!isRecurring}
                  onChange={() => setIsRecurring(false)}
                  className="mr-2"
                />
                Specific Date
              </label>
            </div>
          </FormField>

          {isRecurring ? (
            <>
              <FormField label="Day of Week" required>
                <Select
                  value={dayOfWeek?.toString() || ''}
                  onChange={(e) => setDayOfWeek(e.target.value ? parseInt(e.target.value) : null)}
                  required
                >
                  <option value="">Select day</option>
                  <option value="0">Monday</option>
                  <option value="1">Tuesday</option>
                  <option value="2">Wednesday</option>
                  <option value="3">Thursday</option>
                  <option value="4">Friday</option>
                  <option value="5">Saturday</option>
                  <option value="6">Sunday</option>
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
            </>
          ) : (
            <DatePicker
              label="Date"
              value={specificDate}
              onChange={setSpecificDate}
              required
            />
          )}

          {error && <div className="text-red-600 text-sm mb-4">{error}</div>}

          <div className="flex justify-end gap-2 mt-6">
            <Button type="button" variant="secondary" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? 'Saving...' : 'Save'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

