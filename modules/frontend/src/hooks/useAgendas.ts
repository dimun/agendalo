import { useState, useEffect, useCallback, useMemo } from 'react';
import type { IGateway } from '../gateways/interfaces';
import type { Agenda } from '../types/agenda';
import type { CalendarEvent, Person, Role } from '../types/calendar';
import { agendaEntriesToCalendarEvents } from '../adapters/agendaAdapter';

export function useAgendas(
  gateway: IGateway,
  roleId: string | null,
  startDate: Date,
  endDate: Date
) {
  const [agendas, setAgendas] = useState<Agenda[]>([]);
  const [selectedAgendaId, setSelectedAgendaId] = useState<string | null>(null);
  const [people, setPeople] = useState<Person[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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

  const loadAgendas = useCallback(async () => {
    if (!roleId) {
      setAgendas([]);
      return;
    }
    try {
      setError(null);
      const data = await gateway.getAgendas(roleId);
      setAgendas(data);
      if (data.length > 0 && !selectedAgendaId) {
        setSelectedAgendaId(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agendas');
    }
  }, [gateway, roleId, selectedAgendaId]);

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true);
      setError(null);
      await Promise.all([
        loadPeople(),
        loadRoles(),
        loadAgendas(),
      ]);
      setLoading(false);
    };
    loadAll();
  }, [loadPeople, loadRoles, loadAgendas]);

  const selectedAgenda = useMemo(() => {
    return agendas.find((a) => a.id === selectedAgendaId) || null;
  }, [agendas, selectedAgendaId]);

  const calendarEvents = useMemo(() => {
    if (!selectedAgenda) {
      return [];
    }

    const filteredEntries = selectedAgenda.entries.filter((entry) => {
      const entryDate = new Date(entry.date);
      return entryDate >= startDate && entryDate <= endDate;
    });

    return agendaEntriesToCalendarEvents(filteredEntries, people, roles);
  }, [selectedAgenda, startDate, endDate, people, roles]);

  const refresh = useCallback(() => {
    loadAgendas();
  }, [loadAgendas]);

  return {
    agendas,
    selectedAgenda,
    selectedAgendaId,
    setSelectedAgendaId,
    calendarEvents,
    loading,
    error,
    people,
    roles,
    refresh,
  };
}

