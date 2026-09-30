import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Sparkles, Utensils, Filter, Info, ShieldCheck, AlertTriangle } from 'lucide-react';

export default function Recommendations() {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all'); // all, veg, vegan, gf

  useEffect(() => {
    api
      .get('/recommendations')
      .then((res) => setRecs(res.data))
      .catch((err) => console.error('Failed to load recommendations:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="text-sm text-slate-400 font-medium">Loading clinical recommendations...</div>;
  }

  // Filter food suggestions based on user tag selection
  const filterFoodList = (foods) => {
    if (activeFilter === 'all') return foods;
    return foods.filter((f) => {
      const name = f.name?.toLowerCase() || '';
      if (activeFilter === 'veg') {
        return !name.includes('chicken') && !name.includes('beef') && !name.includes('salmon') && !name.includes('fish') && !name.includes('egg');
      }
      if (activeFilter === 'vegan') {
        return !name.includes('chicken') && !name.includes('beef') && !name.includes('salmon') && !name.includes('fish') && !name.includes('egg') && !name.includes('milk') && !name.includes('yogurt') && !name.includes('cheese');
      }
      if (activeFilter === 'gf') {
        return !name.includes('wheat') && !name.includes('bread') && !name.includes('pasta') && !name.includes('oats');
      }
      return true;
    });
  };

  return (
    <div className="space-y-6">
      {/* Header and Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-emerald-600" />
            Dietary Recommendations & Rule Explanations
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Deterministic food suggestions tied to ML screening outputs and nutrient bioavailability
          </p>
        </div>

        {/* Dietary Preference Filter Tabs */}
        <div className="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl border border-slate-200 self-start sm:self-auto">
          {[
            { id: 'all', label: 'All Items' },
            { id: 'veg', label: 'Vegetarian' },
            { id: 'vegan', label: 'Vegan' },
            { id: 'gf', label: 'Gluten-Free' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id)}
              className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition ${
                activeFilter === tab.id
                  ? 'bg-white text-emerald-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {recs.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 text-sm">
          No active micronutrient deficiencies flagged for targeted intervention.
        </div>
      ) : (
        <div className="space-y-6">
          {recs.map((r, i) => {
            const isHigh = r.payload?.risk_level === 'high';
            const filteredFoods = filterFoodList(r.payload?.suggested_foods || []);

            return (
              <div key={i} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
                {/* Card Title & Risk Badge */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Utensils className="w-5 h-5 text-slate-700" />
                    <h2 className="text-base font-bold text-slate-800 uppercase tracking-wide">
                      Target Intervention: {r.nutrient.replace('_', ' ')}
                    </h2>
                  </div>
                  <span
                    className={`text-xs font-bold px-2.5 py-1 rounded-full uppercase flex items-center gap-1 ${
                      isHigh ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {isHigh ? <AlertTriangle className="w-3.5 h-3.5" /> : <ShieldCheck className="w-3.5 h-3.5" />}
                    {r.payload.risk_level || 'Moderate'} Risk
                  </span>
                </div>

                {/* Rule-Engine Explanation Box */}
                <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-3.5 space-y-1.5">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-700">
                    <Info className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>Clinical Reasoning & Rule Engine Explanation:</span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed pl-5">
                    {r.payload.clinical_tip ||
                      `Assigned due to flagged ${r.nutrient.replace('_', ' ')} vulnerability. Items prioritize high bioavailable density to address identified clinical thresholds.`}
                  </p>
                </div>

                {/* Filtered Food Grid */}
                {filteredFoods.length === 0 ? (
                  <p className="text-xs text-slate-400 py-3 italic">
                    No items match the "{activeFilter}" filter under this nutrient group.
                  </p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-1">
                    {filteredFoods.map((f) => (
                      <div
                        key={f.id || f.name}
                        className="p-3.5 border border-slate-100 rounded-xl bg-slate-50/60 hover:bg-slate-50 transition space-y-1.5"
                      >
                        <div className="flex justify-between items-start">
                          <p className="text-sm font-bold text-slate-800 leading-tight">{f.name}</p>
                          <span className="text-[11px] font-semibold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-100">
                            {f.calories} kcal
                          </span>
                        </div>
                        <p className="text-xs text-slate-400">{f.serving}</p>
                        <div className="pt-1 border-t border-slate-200/60 flex items-center justify-between">
                          <span className="text-[10px] uppercase font-bold text-slate-400">Nutrient Yield</span>
                          <span className="text-xs font-bold text-emerald-700">{f.nutrient_amount}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
} 