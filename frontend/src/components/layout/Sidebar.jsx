import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  User, 
  BookOpen, 
  Stethoscope, 
  Cpu, 
  Sparkles, 
  CalendarDays, 
  LogOut 
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Health Profile', path: '/profile', icon: User },
  { name: 'Food Diary', path: '/diary', icon: BookOpen },
  { name: 'Clinical Inputs', path: '/assessment', icon: Stethoscope },
  { name: 'AI Analysis', path: '/analysis', icon: Cpu },
  { name: 'Recommendations', path: '/recommendations', icon: Sparkles },
  { name: '7-Day Meal Plan', path: '/meal-plan', icon: CalendarDays },
];

export default function Sidebar({ onNavigate }) {
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 h-full bg-white border-r border-slate-200 flex flex-col">
      <div className="p-5 border-b border-slate-100 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-emerald-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
          N
        </div>
        <div>
          <h2 className="text-sm font-bold text-slate-800 leading-tight">Nutrition Intel</h2>
          <p className="text-[11px] text-slate-400 font-medium tracking-wide">MSc Data Science</p>
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => onNavigate && onNavigate()}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-50 text-emerald-700 font-semibold'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center justify-between">
          <div className="truncate mr-2">
            <p className="text-xs font-bold text-slate-800 truncate">{user?.full_name || 'Active User'}</p>
            <p className="text-[11px] text-slate-400 truncate">{user?.email || 'Authenticated'}</p>
          </div>
          <button
            onClick={logout}
            title="Log out"
            className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}