import type { AvailabilityHours, AvailabilityHoursCreate } from '../types/availability';
import type { BusinessServiceHours, BusinessServiceHoursCreate } from '../types/businessHours';
import type { Person, Role, HoursFilters } from '../types/calendar';

export interface IGateway {
  getPeople(): Promise<Person[]>;
  getRoles(): Promise<Role[]>;
  getAvailabilityHours(filters: HoursFilters): Promise<AvailabilityHours[]>;
  createAvailabilityHours(personId: string, data: AvailabilityHoursCreate): Promise<AvailabilityHours>;
  getBusinessServiceHours(filters: HoursFilters): Promise<BusinessServiceHours[]>;
  createBusinessServiceHours(data: BusinessServiceHoursCreate): Promise<BusinessServiceHours>;
}

