import { NavLink, useLocation } from 'react-router-dom';
import { cn } from '@/lib/utils';
import { Home, FileCode, MessageCircle, Play } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/problems', label: 'Problems', icon: FileCode },
  { to: '/chat', label: 'Chat', icon: MessageCircle },
  { to: '/practice', label: 'Practice', icon: Play },
];

export function TopNav() {
  const location = useLocation();

  return (
    <nav className="border-b border-border bg-card/50">
      <div className="flex gap-1 px-6 py-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to;
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={cn(
                'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
}
