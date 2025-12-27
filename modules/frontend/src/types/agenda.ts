export interface AgendaEntry {
  id: string;
  agenda_id: string;
  person_id: string;
  date: string;
  start_time: string;
  end_time: string;
  role_id: string;
}

export interface AgendaCoverage {
  id: string;
  agenda_id: string;
  date: string;
  start_time: string;
  end_time: string;
  role_id: string;
  is_covered: boolean;
  required_person_count: number;
}

export interface Agenda {
  id: string;
  role_id: string;
  status: string;
  created_at: string;
  updated_at: string;
  entries: AgendaEntry[];
  coverage: AgendaCoverage[];
}

export type CalendarMode = 'planning' | 'schedule';

export interface AgendaGenerateRequest {
  role_id: string;
  weeks: number[];
  year: number;
  optimization_strategy: 'maximize_coverage' | 'minimize_gaps' | 'balance_workload';
}

