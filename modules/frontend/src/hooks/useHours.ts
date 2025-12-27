import { useState, useEffect, useCallback, useMemo } from 'react';
import type { IGateway } from '../gateways/interfaces';
import type { AvailabilityHours, AvailabilityHoursCreate } from '../types/availability';
import type { BusinessServiceHours, BusinessServiceHoursCreate } from '../types/businessHours';
import type { CalendarEvent, Person, Role, HoursFilters } from '../types/calendar';
import { toCalendarEvents as availabilityToEvents } from '../adapters/availabilityAdapter';
import { toCalendarEvents as businessToEvents } from '../adapters/businessHoursAdapter';

export function useHours(gateway: IGateway, startDate: Date, endDate: Date) {
  const [people, setPeople] = useState<Person[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [availabilityHours, setAvailabilityHours] = useState<AvailabilityHours[]>([]);
  const [businessServiceHours, setBusinessServiceHours] = useState<BusinessServiceHours[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<string | null>(null);
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null);

  const loadPeople = useCallback(async () => {
    try {
      const data = await gateway.getPeople();
      setPeople(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load people');
    }
  }, [gateway]);

  const loadRoles = useCallback(async () => {
    try {
      const data = await gateway.getRoles();
      setRoles(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load roles');
    }
  }, [gateway]);

  const loadAvailabilityHours = useCallback(async () => {
    try {
      const filters: HoursFilters = {
        role_id: selectedRoleId,
        person_id: selectedPersonId,
        start_date: startDate,
        end_date: endDate,
      };
      const data = await gateway.getAvailabilityHours(filters);
      setAvailabilityHours(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load availability hours');
    }
  }, [gateway, selectedRoleId, selectedPersonId, startDate, endDate]);

  const loadBusinessServiceHours = useCallback(async () => {
    try {
      const filters: HoursFilters = {
        role_id: selectedRoleId,
        start_date: startDate,
        end_date: endDate,
      };
      const data = await gateway.getBusinessServiceHours(filters);
      setBusinessServiceHours(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load business service hours');
    }
  }, [gateway, selectedRoleId, startDate, endDate]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      setError(null);
      await Promise.all([
        loadPeople(),
        loadRoles(),
        loadAvailabilityHours(),
        loadBusinessServiceHours(),
      ]);
      setLoading(false);
    };
    loadAll();
  }, [loadPeople, loadRoles, loadAvailabilityHours, loadBusinessServiceHours]);

  const calendarEvents = useMemo(() => {
    const availabilityEvents = availabilityToEvents(availabilityHours, startDate, endDate);
    const businessEvents = businessToEvents(businessServiceHours, startDate, endDate);
    
    const allEvents = [...availabilityEvents, ...businessEvents];
    
    return allEvents.map((event) => {
      const role = roles.find((r) => r.id === event.role_id);
      const person = event.person_id ? people.find((p) => p.id === event.person_id) : undefined;
      return {
        ...event,
        role_name: role?.name || '',
        person_name: person?.name,
      };
    });
  }, [availabilityHours, businessServiceHours, startDate, endDate, roles, people]);

  const createAvailabilityHours = useCallback(
    async (personId: string, data: AvailabilityHoursCreate) => {
      try {
        const newHours = await gateway.createAvailabilityHours(personId, data);
        setAvailabilityHours((prev) => [...prev, newHours]);
        await loadAvailabilityHours();
        return newHours;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create availability hours');
        throw err;
      }
    },
    [gateway, loadAvailabilityHours]
  );

  const createBusinessServiceHours = useCallback(
    async (data: BusinessServiceHoursCreate) => {
      try {
        const newHours = await gateway.createBusinessServiceHours(data);
        setBusinessServiceHours((prev) => [...prev, newHours]);
        await loadBusinessServiceHours();
        return newHours;
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to create business service hours');
        throw err;
      }
    },
    [gateway, loadBusinessServiceHours]
  );

  return {
    people,
    roles,
    calendarEvents,
    loading,
    error,
    selectedRoleId,
    setSelectedRoleId,
    selectedPersonId,
    setSelectedPersonId,
    createAvailabilityHours,
    createBusinessServiceHours,
    refresh: () => {
      loadAvailabilityHours();
      loadBusinessServiceHours();
    },
  };
}

