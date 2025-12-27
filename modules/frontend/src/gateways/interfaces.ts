import type { AvailabilityHours, AvailabilityHoursCreate } from '../types/availability';
import type { BusinessServiceHours, BusinessServiceHoursCreate, BusinessServiceHoursBulkCreate } from '../types/businessHours';
import type { Person, Role, HoursFilters } from '../types/calendar';
import type { Agenda, AgendaGenerateRequest } from '../types/agenda';

export interface IGateway {
  getPeople(): Promise<Person[]>;
  getRoles(): Promise<Role[]>;
  getAvailabilityHours(filters: HoursFilters): Promise<AvailabilityHours[]>;
  createAvailabilityHours(personId: string, data: AvailabilityHoursCreate): Promise<AvailabilityHours>;
  updateAvailabilityHours?(id: string, data: AvailabilityHours): Promise<AvailabilityHours>;
  getBusinessServiceHours(filters: HoursFilters): Promise<BusinessServiceHours[]>;
  createBusinessServiceHours(data: BusinessServiceHoursCreate): Promise<BusinessServiceHours>;
  createBusinessServiceHoursBulk(data: BusinessServiceHoursBulkCreate): Promise<BusinessServiceHours[]>;
  deleteBusinessServiceHours(id: string): Promise<void>;
  getAgendas(roleId: string, status?: string): Promise<Agenda[]>;
  getAgenda(agendaId: string): Promise<Agenda>;
  generateAgenda(request: AgendaGenerateRequest): Promise<Agenda>;
}

