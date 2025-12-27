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
        const latestAgenda = data.sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )[0];
        setSelectedAgendaId(latestAgenda.id);
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
      const dateString = entry.date.split('T')[0];
      const [year, month, day] = dateString.split('-').map(Number);
      const entryDate = new Date(year, month - 1, day);
      
      const normalizedStartDate = new Date(startDate.getFullYear(), startDate.getMonth(), startDate.getDate());
      const normalizedEndDate = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());
      const normalizedEntryDate = new Date(entryDate.getFullYear(), entryDate.getMonth(), entryDate.getDate());
      
      return normalizedEntryDate >= normalizedStartDate && normalizedEntryDate <= normalizedEndDate;
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

