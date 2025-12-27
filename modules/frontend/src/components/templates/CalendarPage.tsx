import { useState } from 'react';
import { CalendarHeader } from '../organisms/CalendarHeader';
import { CalendarWeekView } from '../organisms/CalendarWeekView';
import { CalendarMonthView } from '../organisms/CalendarMonthView';
import { HoursFormModal } from '../organisms/HoursFormModal';
import { Button } from '../atoms/Button';
import { useCalendar } from '../../hooks/useCalendar';
import { useHours } from '../../hooks/useHours';
import { CalendarEvent, AvailabilityHoursCreate, BusinessServiceHoursCreate } from '../../types/calendar';
import { ApiGateway } from '../../gateways/apiGateway';
import { LocalGateway } from '../../gateways/localGateway';

const USE_LOCAL_GATEWAY = import.meta.env.VITE_USE_LOCAL_GATEWAY === 'true';
const gateway = USE_LOCAL_GATEWAY ? new LocalGateway() : new ApiGateway();

export function CalendarPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'availability' | 'business'>('availability');
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [clickedDate, setClickedDate] = useState<Date | undefined>();
  const [clickedTime, setClickedTime] = useState<{ start: string; end: string } | undefined>();

  const calendar = useCalendar();
  const hours = useHours(gateway, calendar.dateRange.start, calendar.dateRange.end);

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
    setModalOpen(true);
  };

  const handleAddAvailability = () => {
    setModalType('availability');
    setModalOpen(true);
  };

  const handleAddBusinessHours = () => {
    setModalType('business');
    setModalOpen(true);
  };

  const handleSubmit = async (data: AvailabilityHoursCreate | BusinessServiceHoursCreate) => {
    if (modalType === 'availability') {
      if (!hours.selectedPersonId) {
        throw new Error('Please select a person first');
      }
      await hours.createAvailabilityHours(hours.selectedPersonId, data as AvailabilityHoursCreate);
    } else {
      await hours.createBusinessServiceHours(data as BusinessServiceHoursCreate);
    }
    hours.refresh();
  };

  const handleEventDragStart = (event: CalendarEvent, e: React.DragEvent) => {
    e.dataTransfer.setData('eventId', event.id);
    e.dataTransfer.setData('eventType', event.type);
  };

  if (hours.loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-gray-600">Loading calendar...</div>
      </div>
    );
  }

  if (hours.error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg text-red-600">Error: {hours.error}</div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <CalendarHeader
        view={calendar.view}
        onViewChange={calendar.setView}
        formattedDate={calendar.formattedDate}
        onPrevious={calendar.navigatePrevious}
        onNext={calendar.navigateNext}
        onToday={calendar.navigateToToday}
        roles={hours.roles}
        people={hours.people}
        selectedRoleId={hours.selectedRoleId}
        selectedPersonId={hours.selectedPersonId}
        onRoleChange={hours.setSelectedRoleId}
        onPersonChange={hours.setSelectedPersonId}
        showPersonSelector={modalType === 'availability'}
      />

      <div className="flex-1 overflow-hidden flex flex-col">
        {calendar.view === 'week' ? (
          <CalendarWeekView
            currentDate={calendar.currentDate}
            events={hours.calendarEvents}
            onTimeSlotClick={handleTimeSlotClick}
            onEventClick={handleEventClick}
            onEventDragStart={handleEventDragStart}
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
        type={modalType}
        people={hours.people}
        roles={hours.roles}
        initialDate={clickedDate}
        initialTime={clickedTime}
      />
    </div>
  );
}

