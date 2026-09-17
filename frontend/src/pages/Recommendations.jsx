import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Sparkles, Utensils } from 'lucide-react';

export default function Recommendations() {
  const [recs, setRecs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/recommendations').then((res) => setRecs(res.data)).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="text-sm text-slate-400">Loading food suggestions...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dietary Recommendations</h1>
        <p className="text-sm text-slate-500">Nutrient-dense food suggestions matched to identified risks and dietary restrictions</p>
      </div>

      {recs.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 text-xs">
          No active deficiencies flagged for food intervention.
        </div>
      ) : (
        <div className="space-y-6">
          {recs.map((r, i) => (
            <div key={i} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-slate-800 uppercase tracking-wide">
                  Target: {r.nutrient.replace('_', ' ')}
                </h2>
                <span className="text-xs font-semibold px-2 py-0.5 bg-amber-100 text-amber-800 rounded capitalize">
                  {r.payload.risk_level} Risk Targeted
                </span>
              </div>

              <p className="text-xs text-slate-600 bg-emerald-50/60 border border-emerald-100 p-3 rounded-xl font-medium">
                💡 Clinical Strategy: {r.payload.clinical_tip}
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {r.payload.suggested_foods.map((f) => (
                  <div key={f.id} className="p-3 border border-slate-100 rounded-xl bg-slate-50/50">
                    <p className="text-sm font-bold text-slate-800">{f.name}</p>
                    <p className="text-xs text-slate-400">{f.serving} · {f.calories} kcal</p>
                    <p className="text-xs font-semibold text-emerald-700 mt-1">
                      Nutrient Yield: {f.nutrient_amount}
                    </p>
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