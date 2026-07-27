import React, { useState } from 'react';
import { Search, Plus, MoreVertical, ShoppingBag,  Newspaper } from 'lucide-react';
import  type { ScraperItem } from '../types';

export const Scrapers: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [scrapers] = useState<ScraperItem[]>([
    { id: '1', title: 'Amazon Product Scraper', description: 'Collect titles, pricing, ratings, and reviews.', lastRun: 'Today, 10:30 AM', status: 'Active', type: 'amazon' },
    { id: '2', title: 'Daraz Product Scraper', description: 'Extract prices, descriptions, and stock counts.', lastRun: 'Today, 09:15 AM', status: 'Active', type: 'daraz' },
    { id: '3', title: 'LinkedIn Jobs Scraper', description: 'Gather relevant open job roles based on criteria.', lastRun: 'Yesterday, 08:45 PM', status: 'Active', type: 'linkedin' },
    { id: '4', title: 'News Articles Scraper', description: 'Parse recent headline articles across platforms.', lastRun: 'Jul 20, 2026', status: 'Inactive', type: 'news' }
  ]);

  const filteredScrapers = scrapers.filter((item) =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h3 className="text-2xl font-bold text-slate-800">Scrapers</h3>
          <p className="text-xs text-slate-500">Configure and execute automated scripts</p>
        </div>

        <div className="flex gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search scrapers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 border border-slate-200 rounded-lg text-sm focus:outline-none"
            />
          </div>
          <button className="flex items-center gap-1.5 bg-[#5541EC] text-white text-xs font-medium px-4 py-2 rounded-lg hover:bg-[#402ed1] transition">
            <Plus className="w-4 h-4" /> New Scraper
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {filteredScrapers.map((item) => (
          <div key={item.id} className="bg-white border border-slate-200 rounded-xl p-5 flex flex-col justify-between">
            <div>
              <div className="flex justify-between items-start mb-3">
                <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center">
                  {item.type === 'daraz' ? <ShoppingBag className="w-5 h-5 text-orange-500" /> :
                  
                   item.type === 'news' ? <Newspaper className="w-5 h-5 text-emerald-500" /> :
                   <span className="font-bold text-amber-500">A</span>}
                </div>
                <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full ${item.status === 'Active' ? 'bg-emerald-50 text-emerald-600' : 'bg-slate-100 text-slate-500'}`}>
                  {item.status}
                </span>
              </div>
              <h5 className="font-bold text-slate-800 text-sm mb-1">{item.title}</h5>
              <p className="text-slate-500 text-xs mb-4 leading-relaxed">{item.description}</p>
            </div>
            <div>
              <div className="mb-3">
                <span className="text-[10px] text-slate-400 block">Last Executed:</span>
                <span className="text-xs font-medium text-slate-700">{item.lastRun}</span>
              </div>
              <div className="flex gap-2">
                <button className="w-full py-1.5 bg-[#5541EC] text-white rounded-md text-xs font-medium">Run Task</button>
                <button className="p-1.5 border border-slate-200 rounded-md"><MoreVertical className="w-4 h-4" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};