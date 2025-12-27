import { useState, useEffect } from 'react';
import { CalendarHeader } from '../organisms/CalendarHeader';
import { CalendarWeekView } from '../organisms/CalendarWeekView';
import { CalendarMonthView } from '../organisms/CalendarMonthView';
import { HoursFormModal } from '../organisms/HoursFormModal';
import { Tabs } from '../molecules/Tabs';
import { Button } from '../atoms/Button';
import { useCalendar } from '../../hooks/useCalendar';
import { useHours } from '../../hooks/useHours';
import type { CalendarEvent } from '../../types/calendar';
import type { AvailabilityHoursCreate } from '../../types/availability';
import type { BusinessServiceHoursCreate, BusinessServiceHoursBulkCreate } from '../../types/businessHours';
import { ApiGateway } from '../../gateways/apiGateway';
import { LocalGateway } from '../../gateways/localGateway';

const USE_LOCAL_GATEWAY = import.meta.env.VITE_USE_LOCAL_GATEWAY !== 'false' && import.meta.env.VITE_USE_BACKEND_GATEWAY !== 'true';
const gateway = USE_LOCAL_GATEWAY ? new LocalGateway() : new ApiGateway();

export function CalendarPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'availability' | 'business'>('availability');
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [clickedDate, setClickedDate] = useState<Date | undefined>();
  const [clickedTime, setClickedTime] = useState<{ start: string; end: string } | undefined>();
  const [error, setError] = useState<string | null>(null);

  const calendar = useCalendar();
  const hours = useHours(gateway, calendar.dateRange.start, calendar.dateRange.end);

  // Auto-select first role if none selected (obligatory)
  useEffect(() => {
    if (!hours.selectedRoleId && hours.roles.length > 0) {
      hours.setSelectedRoleId(hours.roles[0].id);
    }
  }, [hours.roles, hours.selectedRoleId, hours.setSelectedRoleId]);

  const handleTimeSlotClick = (date: Date, hour: number, minute: number) => {
    const startTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}`;
    const endHour = minute >= 30 ? (hour === 23 ? 0 : hour + 1) : hour;
    const endMinute = minute >= 30 ? 0 : 30;
    const endTime = `${String(endHour).padStart(2, '0')}:${String(endMinute).padStart(2, '0')}`;
    
    setClickedDate(date);
    setClickedTime({ start: startTime, end: endTime });
    setModalOpen(true);
  };

  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
    setModalType(event.type);
    setModalOpen(true);
  };

  const handleBusinessHoursClick = async (event: CalendarEvent) => {
    if (event.type !== 'business') return;
    
    const roleName = event.role_name || 'Business Hours';
    const dayName = event.day_of_week !== null 
      ? ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][event.day_of_week]
      : 'Specific Date';
    
    const confirmMessage = `Delete business hours for ${roleName}?\n\n` +
      `Day: ${dayName}\n` +
      `Time: ${event.start_time} - ${event.end_time}`;
    
    if (window.confirm(confirmMessage)) {
      try {
        setError(null);
        await hours.deleteBusinessServiceHours(event.id);
        hours.refresh();
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete business hours');
      }
    }
  };

  const handleAddAvailability = () => {
    setModalType('availability');
    setModalOpen(true);
  };

  const handleAddBusinessHours = () => {
    setModalType('business');
    setModalOpen(true);
  };

  const handleBulkSubmit = async (data: BusinessServiceHoursBulkCreate) => {
    if (!hours.selectedRoleId) {
      throw new Error('A role must be selected.');
    }
    await hours.createBusinessServiceHoursBulk({ ...data, role_id: hours.selectedRoleId });
    hours.refresh();
  };

  const handleSubmit = async (data: AvailabilityHoursCreate | BusinessServiceHoursCreate, personId?: string, eventId?: string) => {
    if (eventId) {
      // Update existing event
      await hours.updateAvailabilityHours(eventId, data as AvailabilityHoursCreate, personId);
    } else {
      // Create new event
      if (modalType === 'availability') {
        const selectedPersonId = personId || hours.selectedPersonId;
        if (!selectedPersonId) {
          throw new Error('Please select a person');
        }
        await hours.createAvailabilityHours(selectedPersonId, data as AvailabilityHoursCreate);
      } else {
        await hours.createBusinessServiceHours(data as BusinessServiceHoursCreate);
      }
    }
    hours.refresh();
  };

  const handleEventDragStart = (event: CalendarEvent, e: React.DragEvent) => {
    e.dataTransfer.setData('eventId', event.id);
    e.dataTransfer.setData('eventType', event.type);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleEventDrop = async (eventId: string, date: Date, hour: number, minute: number) => {
    try {
      setError(null);
      const event = hours.calendarEvents.find((e) => e.id === eventId);
      if (!event) {
        console.error('Event not found:', eventId);
        return;
      }

      const startTime = `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:00`;
      const [originalStartHour, originalStartMinute] = event.start_time.split(':').map(Number);
      const [originalEndHour, originalEndMinute] = event.end_time.split(':').map(Number);
      
      const originalDuration = (originalEndHour * 60 + originalEndMinute) - (originalStartHour * 60 + originalStartMinute);
      const newEndMinutes = hour * 60 + minute + originalDuration;
      const newEndHour = Math.floor(newEndMinutes / 60);
      const newEndMinute = newEndMinutes % 60;
      const endTime = `${String(newEndHour).padStart(2, '0')}:${String(newEndMinute).padStart(2, '0')}:00`;

      if (event.type === 'availability') {
        // Extract original hours ID from event ID
        // Event IDs can be:
        // - Simple: "ah-1234567890" (for specific_date events)
        // - Composite: "ah-1234567890-2025-01-15" (for recurring/date range events)
        // We need to check if it ends with a date pattern (YYYY-MM-DD) and remove it
        const datePattern = /-\d{4}-\d{2}-\d{2}$/;
        const originalHoursId = datePattern.test(eventId) 
          ? eventId.replace(datePattern, '')
          : eventId;
        
        // For recurring events moved to a specific date, convert to specific_date
        // For non-recurring, update the specific_date
        // Use local date components to avoid timezone issues
        const getLocalDateString = (d: Date): string => {
          const year = d.getFullYear();
          const month = String(d.getMonth() + 1).padStart(2, '0');
          const day = String(d.getDate()).padStart(2, '0');
          return `${year}-${month}-${day}`;
        };
        
        const isRecurring = event.is_recurring;
        const newSpecificDate = isRecurring ? getLocalDateString(date) : (event.specific_date ? getLocalDateString(date) : null);
        
        // Create update data
        const updateData: AvailabilityHoursCreate = {
          role_id: event.role_id,
          start_time: startTime,
          end_time: endTime,
          is_recurring: false, // When dragging, convert to specific date
          day_of_week: null,
          specific_date: newSpecificDate,
          start_date: null,
          end_date: null,
        };
        
        await hours.updateAvailabilityHours(originalHoursId, updateData, event.person_id);
      }
    } catch (err) {
      console.error('Failed to update event:', err);
      setError(err instanceof Error ? err.message : 'Failed to update event');
    }
  };

  if (hours.loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600">Loading calendar...</div>
      </div>
    );
  }

  if (hours.error || error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-red-600">Error: {hours.error || error}</div>
      </div>
    );
  }

  // Ensure a role is always selected (obligatory)
  const effectiveRoleId = hours.selectedRoleId || (hours.roles.length > 0 ? hours.roles[0].id : null);

  const roleTabs = hours.roles.map((role) => ({
    id: role.id,
    label: role.name,
  }));

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <CalendarHeader
        view={calendar.view}
        onViewChange={calendar.setView}
        formattedDate={calendar.formattedDate}
        onPrevious={calendar.navigatePrevious}
        onNext={calendar.navigateNext}
        onToday={calendar.navigateToToday}
        people={hours.people}
        selectedPersonId={hours.selectedPersonId}
        onPersonChange={hours.setSelectedPersonId}
      />

      {hours.roles.length > 0 && (
        <div className="bg-white border-b border-gray-200">
          <Tabs
            tabs={roleTabs}
            activeTabId={effectiveRoleId}
            onTabChange={(roleId) => hours.setSelectedRoleId(roleId)}
            className="px-4"
          />
        </div>
      )}

      <div className="flex-1 overflow-hidden flex flex-col">
        {calendar.view === 'week' ? (
          <CalendarWeekView
            currentDate={calendar.currentDate}
            events={hours.calendarEvents}
            selectedRoleId={effectiveRoleId}
            onTimeSlotClick={handleTimeSlotClick}
            onEventClick={handleEventClick}
            onEventDragStart={handleEventDragStart}
            onEventDrop={handleEventDrop}
            onBusinessHoursClick={handleBusinessHoursClick}
          />
        ) : (
          <CalendarMonthView
            currentDate={calendar.currentDate}
            events={hours.calendarEvents}
            onDayClick={calendar.navigateToDate}
            onEventClick={handleEventClick}
          />
        )}
      </div>

      <div className="bg-white border-t border-gray-200 px-4 py-2 flex justify-end gap-2">
        <Button variant="primary" onClick={handleAddAvailability}>
          Add Availability
        </Button>
        <Button variant="secondary" onClick={handleAddBusinessHours}>
          Add Business Hours
        </Button>
      </div>

      <HoursFormModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setSelectedEvent(null);
          setClickedDate(undefined);
          setClickedTime(undefined);
        }}
        onSubmit={handleSubmit}
        onBulkSubmit={handleBulkSubmit}
        type={modalType}
        people={hours.people}
        roles={hours.roles}
        initialDate={clickedDate}
        initialTime={clickedTime}
        initialEvent={selectedEvent}
      />
    </div>
  );
}

