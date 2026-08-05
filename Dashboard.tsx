import React, { useState } from 'react';
import { Card } from '../components/Card';
import { Button } from '../components/Button/Button';
import { Play } from 'lucide-react';
interface DashboardProps {
  onNavigateToScraper: () => void; 
}
export const Dashboard: React.FC<DashboardProps> = ({ onNavigateToScraper }) =>{
  const [url, setUrl] = useState('');
  const [scraperType, setScraperType] = useState('Product Scraper');

  return (
    
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500">Welcome back! Here is your current scraper state.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Start New Scraping Form (Left Side) */}
        <Card className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-bold text-gray-800 border-b border-gray-100 pb-3">Start New Scraping</h2>
          
          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Target URL</label>
            <input
              type="url"
              placeholder="https://example.com/products"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-600"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-700 mb-1">Select Scraper Type</label>
            <select
              value={scraperType}
              onChange={(e) => setScraperType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-indigo-600"
            >
              <option>Product Scraper</option>
              <option>Real Estate Scraper</option>
              <option>Job Listings Scraper</option>
            </select>
          </div>

          <div className="pt-2">
            <Button>
              <Play className="w-4 h-4 fill-current" />
              Start Scraping
            </Button>
          </div>
        </Card>

        {/* Overview Stats (Right Side) */}
        <Card className="space-y-4">
          <h2 className="text-lg font-bold text-gray-800 border-b border-gray-100 pb-3">Overview</h2>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 p-4 rounded-lg">
              <span className="text-xs text-gray-500 font-medium">Total Jobs</span>
              <p className="text-2xl font-bold text-gray-900 mt-1">128</p>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <span className="text-xs text-gray-500 font-medium">Finished</span>
              <p className="text-2xl font-bold text-green-600 mt-1">89</p>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <span className="text-xs text-gray-500 font-medium">Running</span>
              <p className="text-2xl font-bold text-blue-600 mt-1">3</p>
            </div>
            <div className="bg-slate-50 p-4 rounded-lg">
              <span className="text-xs text-gray-500 font-medium">Failed</span>
              <p className="text-2xl font-bold text-red-600 mt-1">36</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Recent Jobs Table */}
      <Card>
        <h2 className="text-lg font-bold text-gray-800 mb-4">Recent Jobs</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="border-b border-gray-100 text-gray-400 text-xs">
                <th className="pb-3 font-semibold">JOB ID</th>
                <th className="pb-3 font-semibold">NAME</th>
                <th className="pb-3 font-semibold">STATUS</th>
                <th className="pb-3 font-semibold">DATE CREATED</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              <tr>
                <td className="py-3 font-mono text-xs text-gray-500">#1001</td>
                <td className="py-3 font-medium text-gray-800">Product Scraper</td>
                <td className="py-3"><span className="px-2 py-1 bg-blue-50 text-blue-600 text-xs rounded-full font-medium">Running</span></td>
                <td className="py-3 text-gray-500 text-xs">May 18, 2026 11:32 AM</td>
              </tr>
              <tr>
                <td className="py-3 font-mono text-xs text-gray-500">#1002</td>
                <td className="py-3 font-medium text-gray-800">Email Extractor</td>
                <td className="py-3"><span className="px-2 py-1 bg-green-50 text-green-600 text-xs rounded-full font-medium">Completed</span></td>
                <td className="py-3 text-gray-500 text-xs">May 18, 2026 11:30 AM</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="pt-2">
            <Button 
              onClick={onNavigateToScraper}
              className="flex items-center gap-2 bg-[#5541EC] text-white px-4 py-2 rounded-lg"
            >
              <Play className="w-4 h-4" /> Go to Scrapers
            </Button>
          </div>
      </Card>
    </div>
  );
};