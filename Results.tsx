import React, { useState } from 'react';
import { Download, ExternalLink } from 'lucide-react';
import  type{ ResultItem } from '../types';

export const Results: React.FC = () => {
  const [results] = useState<ResultItem[]>([
    { id: '1', title: 'Sony WH-1000XM5 Wireless Headphones', price: '$347.00', site: 'Amazon', timestamp: 'Today, 10:35 AM' },
    { id: '2', title: 'Frontend Developer Remote Role', price: 'Part-time', site: 'LinkedIn', timestamp: 'Today, 09:20 AM' },
    { id: '3', title: 'Samsung Galaxy S24 Ultra 512GB', price: '$1,199.00', site: 'Daraz', timestamp: 'Yesterday, 06:10 PM' },
    { id: '4', title: 'TCL WH-1000XM5  Headphones', price: '$368.00', site: 'Amazon', timestamp: 'Today, 10:35 AM' },
    { id: '5', title: 'Backend Developer Remote Role', price: 'Full-time', site: 'LinkedIn', timestamp: 'Today, 09:20 AM' },
    { id: '6', title: 'Iphone 17 pro max 512GB', price: '$2,199.00', site: 'Daraz', timestamp: 'Yesterday, 04:10 PM' }
  ]);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-2xl font-bold text-slate-800">Scraped Results</h3>
          <p className="text-xs text-slate-500">Collected datasets and exports</p>
        </div>
        <button className="flex items-center gap-2 bg-[#5541EC] text-white text-xs font-medium px-4 py-2 rounded-lg hover:bg-[#402ed1]">
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      <div className="bg-white p-6 border border-slate-200 rounded-xl space-y-3">
        {results.map((item) => (
          <div key={item.id} className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-slate-100 text-sm">
            <div>
              <p className="font-semibold text-slate-800">{item.title}</p>
              <span className="text-xs text-slate-400">{item.site} • {item.timestamp}</span>
            </div>
            <div className="flex items-center gap-4">
              <span className="font-bold text-[#5541EC]">{item.price}</span>
              <button className="text-slate-400 hover:text-slate-600"><ExternalLink className="w-4 h-4" /></button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};