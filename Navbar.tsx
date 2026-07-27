import React from 'react';
import { Bell, User as UserIcon } from 'lucide-react';
import type { User } from '../types';

export const Navbar: React.FC<{ user: User | null }> = ({ user }) => {
  return (
    <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-8">
      <div className="text-sm font-medium text-gray-500">
        Web Scraping Management Portal
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-50">
          <Bell className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-3 pl-4 border-l border-gray-200">
          <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center">
            <UserIcon className="w-4 h-4" />
          </div>
          <span className="text-sm font-semibold text-gray-700">{user?.name || 'User'}</span>
        </div>
      </div>
    </header>
  );
};