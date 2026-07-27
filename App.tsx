import React, { useState } from 'react';
import { AuthLayout } from './layouts/AuthLayout';
import { MainLayout } from './layouts/MainLayout';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { Scrapers } from './pages/Scraper';
import { Jobs } from './pages/JobQueues';
import { Results } from './pages/Results';
import { Settings } from './pages/Settings';
import type { User } from './types';

export default function App() {
  // 1. Initial State null rakhne se banda directly Login Page par jayega
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  
  // Default tab Scrapers rakhein (kyunki ab pehla option Scraper hai)
  const [activeTab, setActiveTab] = useState<string>('scrapers');

  const handleLoginSuccess = (user: User) => {
    setCurrentUser(user);
  };

  const handleLogout = () => {
    setCurrentUser(null);
  };

  // 2. Agar user logged in nahi hai, toh ONLY Login screen dikhegi
  if (!currentUser) {
    return (
      <AuthLayout>
        <Login onLoginSuccess={handleLoginSuccess} />
      </AuthLayout>
    );
  }

  // 3. Login ke Baad Main Application Views
  return (
    <MainLayout
      activeTab={activeTab}
      setActiveTab={setActiveTab}
      user={currentUser}
      onLogout={handleLogout}
    >
      {activeTab === 'scrapers' && <Scrapers />}
      {activeTab === 'jobs' && <Jobs />}
      {activeTab === 'results' && <Results />}
      {activeTab === 'dashboard' && (
        <Dashboard onNavigateToScraper={() => setActiveTab('scrapers')} />
      )}
      {activeTab === 'settings' && <Settings />}
    </MainLayout>
  );
}