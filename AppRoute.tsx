import React from 'react';
import { Dashboard } from '../pages/Dashboard';
import { Scrapers } from '../pages/Scraper';
import { Jobs } from '../pages/JobQueues';
import { Results } from '../pages/Results';
import { Settings } from '../pages/Settings';

interface AppRoutesProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const AppRoutes: React.FC<AppRoutesProps> = ({ activeTab, setActiveTab }) => {
  switch (activeTab) {
    case 'dashboard':
      return <Dashboard onNavigateToScraper={() => setActiveTab('scraper')} />;
    case 'scrapers':
      return <Scrapers />;
    case 'jobs':
      return <Jobs />;
    case 'results':
      return <Results />;
    case 'settings':
      return <Settings />;
    default:
      return <Dashboard onNavigateToScraper={() => setActiveTab('scrapers')} />;
  }
};