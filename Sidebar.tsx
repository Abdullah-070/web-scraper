import React from 'react';
import { LayoutGrid, CheckSquare, FileText, Download, Settings, LogOut } from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab, onLogout }) => {
 const menuItems = [
  { id: 'scrapers', label: 'Scrapers', icon: LayoutGrid }, // 👈 Dashboard ki jagah Scraper
  { id: 'jobs', label: 'Job Queue', icon: CheckSquare },
  { id: 'results', label: 'Results', icon: FileText },
  { id: 'dashboard', label: 'Dashboard', icon: Download }, // 👈 Export ki jagah Dashboard
  { id: 'settings', label: 'Settings', icon: Settings },
];

  return (
    <aside className="w-64 bg-[#0f172a] text-white min-h-screen flex flex-col justify-between p-4">
      <div>
        {/* Brand Logo */}
        <div className="flex items-center gap-3 px-3 py-4 mb-6">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center font-bold text-lg">
            S
          </div>
          <span className="font-bold text-xl tracking-tight">SANESTIX</span>
        </div>

        {/* Navigation Links */}
        <nav className="space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`}
              >
                
                <Icon className="w-5 h-5" />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Logout Action */}
      <button
        onClick={onLogout}
        className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-colors w-full"
      >
        <LogOut className="w-5 h-5" />
        Logout
      </button>
    </aside>
  );
};