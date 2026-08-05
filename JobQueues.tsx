import React, { useState } from 'react';
import { RefreshCw } from 'lucide-react';
import  type { JobItem } from '../types';

export const Jobs: React.FC = () => {
  const [jobs] = useState<JobItem[]>([
    { id: 'JOB-101', scraper: 'Amazon Scraper', status: 'Running', progress: '75%', time: '10 mins ago' },
    { id: 'JOB-102', scraper: 'LinkedIn Jobs', status: 'Queued', progress: '0%', time: '2 mins ago' },
    { id: 'JOB-103', scraper: 'Daraz Scraper', status: 'Completed', progress: '100%', time: '1 hour ago' },
    { id: 'JOB-104', scraper: 'News Articles Scraper', status: 'Failed', progress: '20%', time: '3 hours ago' },
     { id: 'JOB-105', scraper: 'ShopCart Scraper', status: 'Completed', progress: '100%', time: '1 hour ago' },
    { id: 'JOB-106', scraper: 'News Scraper', status: 'Failed', progress: '20%', time: '3 hours ago' },
  ]);

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-2xl font-bold text-slate-800">Job Queues</h3>
        <p className="text-xs text-slate-500">Live view of current and completed extraction tasks</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 border-b border-slate-200 text-xs font-semibold text-slate-500">
              <th className="p-4">Job ID</th>
              <th className="p-4">Scraper Name</th>
              <th className="p-4">Status</th>
              <th className="p-4">Progress</th>
              <th className="p-4">Started</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
            {jobs.map((job) => (
              <tr key={job.id} className="hover:bg-slate-50 transition">
                <td className="p-4 font-mono font-medium text-xs">{job.id}</td>
                <td className="p-4 font-semibold">{job.scraper}</td>
                <td className="p-4">
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                    job.status === 'Running' ? 'bg-blue-50 text-blue-600' :
                    job.status === 'Completed' ? 'bg-emerald-50 text-emerald-600' :
                    job.status === 'Failed' ? 'bg-red-50 text-red-600' : 'bg-amber-50 text-amber-600'
                  }`}>
                    {job.status}
                  </span>
                </td>
                <td className="p-4">
                  <div className="w-32 bg-slate-100 h-2 rounded-full overflow-hidden">
                    <div className="bg-[#5541EC] h-full" style={{ width: job.progress }}></div>
                  </div>
                </td>
                <td className="p-4 text-xs text-slate-400">{job.time}</td>
                <td className="p-4 text-right">
                  <button className="p-1.5 text-slate-400 hover:text-[#5541EC]"><RefreshCw className="w-4 h-4" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};