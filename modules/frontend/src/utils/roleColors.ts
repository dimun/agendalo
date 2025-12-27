export const ROLE_COLORS = [
  { primary: '#3b82f6', light: '#dbeafe', text: '#1e40af' },
  { primary: '#10b981', light: '#d1fae5', text: '#065f46' },
  { primary: '#f59e0b', light: '#fef3c7', text: '#92400e' },
  { primary: '#ef4444', light: '#fee2e2', text: '#991b1b' },
  { primary: '#8b5cf6', light: '#ede9fe', text: '#5b21b6' },
  { primary: '#ec4899', light: '#fce7f3', text: '#9f1239' },
  { primary: '#06b6d4', light: '#cffafe', text: '#0e7490' },
  { primary: '#84cc16', light: '#ecfccb', text: '#365314' },
  { primary: '#f97316', light: '#ffedd5', text: '#9a3412' },
  { primary: '#6366f1', light: '#e0e7ff', text: '#3730a3' },
  { primary: '#14b8a6', light: '#ccfbf1', text: '#0f766e' },
  { primary: '#a855f7', light: '#f3e8ff', text: '#6b21a8' },
  { primary: '#f43f5e', light: '#ffe4e6', text: '#9f1239' },
  { primary: '#0ea5e9', light: '#e0f2fe', text: '#0c4a6e' },
  { primary: '#22c55e', light: '#dcfce7', text: '#14532d' },
  { primary: '#eab308', light: '#fef9c3', text: '#713f12' },
  { primary: '#fb923c', light: '#fed7aa', text: '#7c2d12' },
  { primary: '#a78bfa', light: '#ede9fe', text: '#5b21b6' },
  { primary: '#fb7185', light: '#ffe4e6', text: '#9f1239' },
  { primary: '#34d399', light: '#d1fae5', text: '#065f46' },
];

export const getRoleColor = (roleId: string): typeof ROLE_COLORS[0] => {
  let hash = 0;
  for (let i = 0; i < roleId.length; i++) {
    hash = roleId.charCodeAt(i) + ((hash << 5) - hash);
  }
  const index = Math.abs(hash) % ROLE_COLORS.length;
  return ROLE_COLORS[index];
};

