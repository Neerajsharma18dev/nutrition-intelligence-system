import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { RefreshCw, CalendarDays } from 'lucide-react';

export default function MealPlan() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchPlan = async () => {
    try {
      const res = await api.get('/meal-plan');
      setPlan(res.data.plan);
    } catch {}
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  const handleRegenerate = async () => {
    setLoading(true);
    try {
      const res = await api.post('/meal-plan/regenerate');
      setPlan(res.data.plan);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Personalised 7-Day Meal Schedule</h1>
          <p className="text-sm text-slate-500">Automated balanced meal distribution conforming to profile restrictions</p>
        </div>
        <button
          onClick={handleRegenerate}
          disabled={loading}
          className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Rebuilding Schedule...' : 'Regenerate 7 Days'}</span>
        </button>
      </div>

      {!plan ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 text-xs">
          No meal schedule active. Click Regenerate to generate your first schedule.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plan.map((d) => (
            <div key={d.day} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-sm font-bold text-slate-800">Day {d.day}</span>
                <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  {d.daily_calories} kcal
                </span>
              </div>

              <div className="space-y-2 text-xs">
                {Object.entries(d.meals).map(([slot, item]) => (
                  <div key={slot} className="p-2 bg-slate-50 rounded-lg">
                    <p className="font-bold text-slate-700 uppercase text-[10px] tracking-wider text-slate-400">
                      {slot}
                    </p>
                    <p className="font-semibold text-slate-800 mt-0.5">{item.name}</p>
                    <p className="text-slate-400 text-[11px]">{item.serving} · {item.calories} kcal</p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}