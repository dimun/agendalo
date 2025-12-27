import { getRoleColor } from '../../utils/roleColors';

interface Tab {
  id: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  activeTabId: string | null;
  onTabChange: (tabId: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTabId, onTabChange, className = '' }: TabsProps) {
  return (
    <div className={`flex border-b border-gray-200 ${className}`}>
      {tabs.map((tab) => {
        const isActive = activeTabId === tab.id;
        const roleColor = getRoleColor(tab.id);
        return (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              px-6 py-3 text-sm font-medium transition-colors duration-200
              border-b-2 -mb-px
              ${
                isActive
                  ? ''
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
            style={
              isActive
                ? {
                    borderBottomColor: roleColor.primary,
                    color: roleColor.primary,
                  }
                : undefined
            }
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}

