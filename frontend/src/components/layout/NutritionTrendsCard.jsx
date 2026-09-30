import React, { useState, useEffect } from 'react';
import api from '../../api/client';
import { TrendingUp, Info, Activity } from 'lucide-react';

export default function NutritionTrendsCard() {
  const [trendData, setTrendData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        const res = await api.get('/food-diary/history/trends');
        setTrendData(res.data);
      } catch (err) {
        console.error('Failed to load history trends:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTrends();
  }, []);

  if (loading) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm animate-pulse space-y-3">
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-28 bg-slate-100 rounded-xl"></div>
      </div>
    );
  }

  // Fallback View: Jab user ke paas < 2 din ka record ho
  if (!trendData?.has_sufficient_data) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-3">
        <div className="flex items-center gap-2 text-slate-800 font-bold text-sm">
          <TrendingUp className="w-4 h-4 text-emerald-600" />
          <span>7-Day Nutritional Trends & Adherence</span>
        </div>
        <div className="bg-slate-50 border border-slate-100 rounded-xl p-5 text-center space-y-2">
          <Info className="w-5 h-5 text-slate-400 mx-auto" />
          <p className="text-xs text-slate-600 font-medium max-w-md mx-auto">
            {trendData?.message || 'Insufficient historical entries. Log meals for at least 2 distinct days in your Food Diary to unlock multi-day analytics.'}
          </p>
          <span className="inline-block text-[11px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full">
            Logged Days: {trendData?.days_recorded || 0} / 2 required
          </span>
        </div>
      </div>
    );
  }

  // Active View: Jab user ke paas 2 ya usse zyada din ka data ho
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2 text-slate-800 font-bold text-sm">
          <Activity className="w-4 h-4 text-emerald-600" />
          <span>7-Day Nutritional History & Adherence</span>
        </div>
        <span className="text-xs text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full font-medium">
          {trendData.days_recorded} Days Tracked
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {trendData.trends.map((day) => (
          <div key={day.date} className="bg-slate-50 border border-slate-100 p-3 rounded-xl space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-700">
              <span>{day.date}</span>
              <span className="text-emerald-600">{day.adherence_score}% Target</span>
            </div>
            
            {/* Adherence Progress Bar */}
            <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
              <div
                className="bg-emerald-500 h-1.5 rounded-full transition-all duration-300"
                style={{ width: `${day.adherence_score}%` }}
              ></div>
            </div>

            <div className="grid grid-cols-3 gap-1 pt-1 text-[11px] text-slate-500">
              <div>
                <p className="text-[10px] uppercase text-slate-400">Energy</p>
                <p className="font-semibold text-slate-700">{day.calories} kcal</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-slate-400">Protein</p>
                <p className="font-semibold text-slate-700">{day.protein_g}g</p>
              </div>
              <div>
                <p className="text-[10px] uppercase text-slate-400">Iron</p>
                <p className="font-semibold text-slate-700">{day.iron_mg}mg</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}