import { CalendarView, Person, Role } from '../../types/calendar';
import { Button } from '../atoms/Button';
import { Select } from '../atoms/Select';

interface CalendarHeaderProps {
  view: CalendarView;
  onViewChange: (view: CalendarView) => void;
  formattedDate: string;
  onPrevious: () => void;
  onNext: () => void;
  onToday: () => void;
  roles: Role[];
  people: Person[];
  selectedRoleId: string | null;
  selectedPersonId: string | null;
  onRoleChange: (roleId: string | null) => void;
  onPersonChange: (personId: string | null) => void;
  showPersonSelector?: boolean;
}

export function CalendarHeader({
  view,
  onViewChange,
  formattedDate,
  onPrevious,
  onNext,
  onToday,
  roles,
  people,
  selectedRoleId,
  selectedPersonId,
  onRoleChange,
  onPersonChange,
  showPersonSelector = false,
}: CalendarHeaderProps) {
  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-semibold text-gray-900">Calendar</h1>
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={onToday}>
              Today
            </Button>
            <div className="flex items-center gap-1">
              <Button variant="ghost" onClick={onPrevious}>
                ‹
              </Button>
              <Button variant="ghost" onClick={onNext}>
                ›
              </Button>
            </div>
            <span className="text-lg font-medium text-gray-700">{formattedDate}</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 border rounded-md">
            <button
              onClick={() => onViewChange('week')}
              className={`px-4 py-2 text-sm font-medium ${
                view === 'week'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Week
            </button>
            <button
              onClick={() => onViewChange('month')}
              className={`px-4 py-2 text-sm font-medium ${
                view === 'month'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Month
            </button>
          </div>

          <Select
            value={selectedRoleId || ''}
            onChange={(e) => onRoleChange(e.target.value || null)}
            className="w-48"
          >
            <option value="">All Roles</option>
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </Select>

          {showPersonSelector && (
            <Select
              value={selectedPersonId || ''}
              onChange={(e) => onPersonChange(e.target.value || null)}
              className="w-48"
            >
              <option value="">All People</option>
              {people.map((person) => (
                <option key={person.id} value={person.id}>
                  {person.name}
                </option>
              ))}
            </Select>
          )}
        </div>
      </div>
    </div>
  );
}

