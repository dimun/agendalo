import type { IGateway } from './interfaces';
import type { AvailabilityHours, AvailabilityHoursCreate } from '../types/availability';
import type { BusinessServiceHours, BusinessServiceHoursCreate, BusinessServiceHoursBulkCreate } from '../types/businessHours';
import type { Person, Role, HoursFilters } from '../types/calendar';
import type { Agenda, AgendaGenerateRequest } from '../types/agenda';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export class ApiGateway implements IGateway {
  private async fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status} ${response.statusText}`);
    }

    if (response.status === 204) {
      return undefined as T;
    }

    const text = await response.text();
    if (!text) {
      return undefined as T;
    }

    return JSON.parse(text);
  }

  async getPeople(): Promise<Person[]> {
    return this.fetchJson<Person[]>(`${API_BASE_URL}/people`);
  }

  async getRoles(): Promise<Role[]> {
    return this.fetchJson<Role[]>(`${API_BASE_URL}/roles`);
  }

  async getAvailabilityHours(filters: HoursFilters): Promise<AvailabilityHours[]> {
    const params = new URLSearchParams();
    if (filters.role_id) {
      params.append('role_id', filters.role_id);
    }
    if (filters.start_date && filters.end_date) {
      params.append('start_date', filters.start_date.toISOString().split('T')[0]);
      params.append('end_date', filters.end_date.toISOString().split('T')[0]);
    }

    if (filters.person_id) {
      return this.fetchJson<AvailabilityHours[]>(
        `${API_BASE_URL}/people/${filters.person_id}/availability-hours`
      );
    }

    if (params.toString()) {
      return this.fetchJson<AvailabilityHours[]>(`${API_BASE_URL}/availability-hours?${params}`);
    }

    throw new Error('Either role_id or both start_date and end_date must be provided');
  }

  async createAvailabilityHours(
    personId: string,
    data: AvailabilityHoursCreate
  ): Promise<AvailabilityHours> {
    return this.fetchJson<AvailabilityHours>(
      `${API_BASE_URL}/people/${personId}/availability-hours`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  async getBusinessServiceHours(filters: HoursFilters): Promise<BusinessServiceHours[]> {
    const params = new URLSearchParams();
    if (filters.role_id) {
      params.append('role_id', filters.role_id);
    }
    if (filters.start_date && filters.end_date) {
      params.append('start_date', filters.start_date.toISOString().split('T')[0]);
      params.append('end_date', filters.end_date.toISOString().split('T')[0]);
    }

    const queryString = params.toString();
    const url = queryString
      ? `${API_BASE_URL}/business-service-hours?${queryString}`
      : `${API_BASE_URL}/business-service-hours`;

    return this.fetchJson<BusinessServiceHours[]>(url);
  }

  async createBusinessServiceHours(
    data: BusinessServiceHoursCreate
  ): Promise<BusinessServiceHours> {
    return this.fetchJson<BusinessServiceHours>(`${API_BASE_URL}/business-service-hours`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async createBusinessServiceHoursBulk(
    data: BusinessServiceHoursBulkCreate
  ): Promise<BusinessServiceHours[]> {
    return this.fetchJson<BusinessServiceHours[]>(`${API_BASE_URL}/business-service-hours/bulk`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async deleteBusinessServiceHours(id: string): Promise<void> {
    await this.fetchJson<void>(`${API_BASE_URL}/business-service-hours/${id}`, {
      method: 'DELETE',
    });
  }

  async getAgendas(roleId: string, status?: string): Promise<Agenda[]> {
    const params = new URLSearchParams();
    params.append('role_id', roleId);
    if (status) {
      params.append('status', status);
    }
    return this.fetchJson<Agenda[]>(`${API_BASE_URL}/agendas?${params}`);
  }

  async getAgenda(agendaId: string): Promise<Agenda> {
    return this.fetchJson<Agenda>(`${API_BASE_URL}/agendas/${agendaId}`);
  }

  async generateAgenda(request: AgendaGenerateRequest): Promise<Agenda> {
    return this.fetchJson<Agenda>(`${API_BASE_URL}/agendas/generate`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }
}

