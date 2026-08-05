import React, { useState } from 'react';

export const Settings: React.FC = () => {
  const [proxy, setProxy] = useState('http://proxy.sanestix.internal:8080');
  const [concurrentLimit, setConcurrentLimit] = useState(5);
  const [saveMessage, setSaveMessage] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaveMessage(true);
    setTimeout(() => setSaveMessage(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h3 className="text-2xl font-bold text-slate-800">Settings</h3>
        <p className="text-xs text-slate-500">Configure client extraction defaults</p>
      </div>

      <form onSubmit={handleSave} className="bg-white p-6 border border-slate-200 rounded-xl space-y-4">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Proxy Endpoint</label>
          <input
            type="text"
            value={proxy}
            onChange={(e) => setProxy(e.target.value)}
            className="w-full p-2 border border-slate-200 rounded-lg text-sm"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">Max Concurrent Scrapers</label>
          <input
            type="number"
            value={concurrentLimit}
            onChange={(e) => setConcurrentLimit(Number(e.target.value))}
            className="w-full p-2 border border-slate-200 rounded-lg text-sm"
          />
        </div>

        {saveMessage && (
          <p className="text-xs text-emerald-600 font-medium">Settings updated successfully!</p>
        )}

        <button type="submit" className="bg-[#5541EC] text-white text-xs font-medium px-5 py-2.5 rounded-lg hover:bg-[#402ed1]">
          Save Preferences
        </button>
      </form>
    </div>
  );
};