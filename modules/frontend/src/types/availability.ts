export interface AvailabilityHours {
  id: string;
  person_id: string;
  role_id: string;
  day_of_week: number | null;
  start_time: string;
  end_time: string;
  start_date: string | null;
  end_date: string | null;
  is_recurring: boolean;
  specific_date: string | null;
}

export interface AvailabilityHoursCreate {
  role_id: string;
  day_of_week: number | null;
  start_time: string;
  end_time: string;
  start_date: string | null;
  end_date: string | null;
  is_recurring: boolean;
  specific_date: string | null;
}

