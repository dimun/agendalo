import type { IGateway } from './interfaces';
import type { AvailabilityHours, AvailabilityHoursCreate } from '../types/availability';
import type { BusinessServiceHours, BusinessServiceHoursCreate, BusinessServiceHoursBulkCreate } from '../types/businessHours';
import type { Person, Role, HoursFilters } from '../types/calendar';

const mockPeople: Person[] = [
  { id: '1', name: 'John Doe', email: 'john@example.com' },
  { id: '2', name: 'Jane Smith', email: 'jane@example.com' },
  { id: '3', name: 'Bob Johnson', email: 'bob@example.com' },
];

const mockRoles: Role[] = [
  { id: '1', name: 'Doctor', description: 'Medical doctor' },
  { id: '2', name: 'Nurse', description: 'Registered nurse' },
  { id: '3', name: 'Receptionist', description: 'Front desk staff' },
];

const mockAvailabilityHours: AvailabilityHours[] = [];
const mockBusinessServiceHours: BusinessServiceHours[] = [];

export class LocalGateway implements IGateway {
  async getPeople(): Promise<Person[]> {
    return Promise.resolve([...mockPeople]);
  }

  async getRoles(): Promise<Role[]> {
    return Promise.resolve([...mockRoles]);
  }

  async getAvailabilityHours(filters: HoursFilters): Promise<AvailabilityHours[]> {
    let filtered = [...mockAvailabilityHours];

    if (filters.role_id) {
      filtered = filtered.filter((ah) => ah.role_id === filters.role_id);
    }

    if (filters.person_id) {
      filtered = filtered.filter((ah) => ah.person_id === filters.person_id);
    }

    if (filters.start_date && filters.end_date) {
      filtered = filtered.filter((ah) => {
        if (ah.specific_date) {
          const date = new Date(ah.specific_date);
          return date >= filters.start_date! && date <= filters.end_date!;
        }
        if (ah.start_date && ah.end_date) {
          const start = new Date(ah.start_date);
          const end = new Date(ah.end_date);
          return !(end < filters.start_date! || start > filters.end_date!);
        }
        return true;
      });
    }

    return Promise.resolve(filtered);
  }

  async createAvailabilityHours(
    personId: string,
    data: AvailabilityHoursCreate
  ): Promise<AvailabilityHours> {
    const newHours: AvailabilityHours = {
      id: `ah-${Date.now()}`,
      person_id: personId,
      ...data,
    };
    mockAvailabilityHours.push(newHours);
    return Promise.resolve(newHours);
  }

  async getBusinessServiceHours(filters: HoursFilters): Promise<BusinessServiceHours[]> {
    let filtered = [...mockBusinessServiceHours];

    if (filters.role_id) {
      filtered = filtered.filter((bsh) => bsh.role_id === filters.role_id);
    }

    if (filters.start_date && filters.end_date) {
      filtered = filtered.filter((bsh) => {
        if (bsh.specific_date) {
          const date = new Date(bsh.specific_date);
          return date >= filters.start_date! && date <= filters.end_date!;
        }
        if (bsh.start_date && bsh.end_date) {
          const start = new Date(bsh.start_date);
          const end = new Date(bsh.end_date);
          return !(end < filters.start_date! || start > filters.end_date!);
        }
        return true;
      });
    }

    return Promise.resolve(filtered);
  }

  async createBusinessServiceHours(
    data: BusinessServiceHoursCreate
  ): Promise<BusinessServiceHours> {
    const newHours: BusinessServiceHours = {
      id: `bsh-${Date.now()}`,
      ...data,
    };
    mockBusinessServiceHours.push(newHours);
    return Promise.resolve(newHours);
  }

  async updateAvailabilityHours(
    id: string,
    data: AvailabilityHours
  ): Promise<AvailabilityHours> {
    const index = mockAvailabilityHours.findIndex((ah) => ah.id === id);
    if (index === -1) {
      throw new Error('Availability hours not found');
    }
    mockAvailabilityHours[index] = data;
    return Promise.resolve(data);
  }

  async createBusinessServiceHoursBulk(
    data: BusinessServiceHoursBulkCreate
  ): Promise<BusinessServiceHours[]> {
    const dayMap: Record<string, number[]> = {
      'mon-fri': [0, 1, 2, 3, 4],
      'mon-sat': [0, 1, 2, 3, 4, 5],
      'all': [0, 1, 2, 3, 4, 5, 6],
    };

    const days = dayMap[data.days.toLowerCase()] || [];
    const created: BusinessServiceHours[] = [];

    days.forEach((dayOfWeek) => {
      const newHours: BusinessServiceHours = {
        id: `bsh-${Date.now()}-${dayOfWeek}`,
        role_id: data.role_id,
        day_of_week: dayOfWeek,
        start_time: data.start_time,
        end_time: data.end_time,
        start_date: data.start_date,
        end_date: data.end_date,
        is_recurring: true,
        specific_date: null,
      };
      mockBusinessServiceHours.push(newHours);
      created.push(newHours);
    });

    return Promise.resolve(created);
  }

  async deleteBusinessServiceHours(id: string): Promise<void> {
    const index = mockBusinessServiceHours.findIndex((bsh) => bsh.id === id);
    if (index === -1) {
      throw new Error('Business service hours not found');
    }
    mockBusinessServiceHours.splice(index, 1);
    return Promise.resolve();
  }
}

