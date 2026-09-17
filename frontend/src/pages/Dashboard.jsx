import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../api/client';
import { Cpu, ArrowRight, CheckCircle2, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const [profile, setProfile] = useState(null);
  const [latestPred, setLatestPred] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [pRes, predRes] = await Promise.allSettled([
          api.get('/profile'),
          api.get('/predict/latest'),
        ]);
        if (pRes.status === 'fulfilled') setProfile(pRes.value.data);
        if (predRes.status === 'fulfilled') setLatestPred(predRes.value.data);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return <div className="text-sm text-slate-400 font-medium">Loading clinical workspace...</div>;
  }

  return (
    <div className="w-full space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">Clinical Dashboard</h1>
        <p className="text-sm text-slate-500 mt-1">Multi-nutrient risk overview and screening inference summary</p>
      </div>

      {/* Top 3 Stat Cards - 1 col on mobile, 3 cols on desktop, auto-scaling */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Composite Health Index</p>
          <div className="my-3 flex items-baseline gap-2">
            <span className="text-3xl sm:text-4xl font-extrabold text-slate-900">
              {latestPred ? `${latestPred.overall_score}/100` : 'Pending'}
            </span>
            {latestPred && (
              <span className="text-xs font-semibold text-emerald-600 flex items-center gap-0.5">
                <TrendingUp className="w-3.5 h-3.5" /> Baseline
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500">Multi-nutrient status aggregation</p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Health Profile Status</p>
          <div className="my-3 flex items-center gap-2">
            {profile ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
                <span className="text-lg sm:text-xl font-bold text-slate-800">
                  {profile.gender.toUpperCase()}, {profile.age} yrs
                </span>
              </>
            ) : (
              <span className="text-lg font-bold text-amber-600">Incomplete Profile</span>
            )}
          </div>
          <p className="text-xs text-slate-500">
            {profile ? `BMI: ${profile.bmi} (${profile.activity_level})` : 'Profile required before prediction'}
          </p>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between">
          <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Active ML Pipelines</p>
          <div className="my-3 flex items-center gap-3">
            <span className="text-3xl sm:text-4xl font-extrabold text-emerald-600">5</span>
            <span className="text-xs font-medium text-slate-600 leading-snug">Classifiers operational (RF + SHAP)</span>
          </div>
          <p className="text-xs text-slate-500">Trained on clinical cutoffs & RDAs</p>
        </div>
      </div>

      {/* Inference Action Banner */}
      <div className="w-full bg-gradient-to-r from-emerald-600 via-teal-600 to-emerald-700 text-white p-6 sm:p-7 rounded-2xl shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-5">
        <div className="space-y-1">
          <h2 className="text-lg sm:text-xl font-bold">Run Nutrition Intelligence Inference</h2>
          <p className="text-sm text-emerald-100 max-w-3xl leading-relaxed">
            Process 31-dimensional patient vector (Diet, Symptoms, Blood Labs) across 5 Random Forest models with signed SHAP factor explanations.
          </p>
        </div>
        <Link
          to="/analysis"
          className="px-6 py-3 bg-white text-emerald-800 rounded-xl text-sm font-bold hover:bg-emerald-50 transition shrink-0 flex items-center gap-2 shadow-sm"
        >
          <Cpu className="w-4 h-4 text-emerald-700" />
          <span>Launch AI Analysis</span>
        </Link>
      </div>

      {/* Latest Prediction Results Card */}
      <div className="w-full bg-white rounded-2xl border border-slate-200 p-6 sm:p-7 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
          <div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900">Latest Micronutrient Screening</h2>
            <p className="text-xs text-slate-400 mt-0.5">Automated deficiency risk breakdown per model</p>
          </div>
          <Link to="/analysis" className="text-xs font-bold text-emerald-600 hover:text-emerald-700 flex items-center gap-1">
            View full SHAP decomposition <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {latestPred ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-5 gap-4">
            {latestPred.results.map((r) => {
              const isHigh = r.risk_level === 'high';
              const isMod = r.risk_level === 'moderate';
              return (
                <div
                  key={r.nutrient}
                  className={`p-4 rounded-xl border transition-all ${
                    isHigh
                      ? 'bg-rose-50/60 border-rose-200'
                      : isMod
                      ? 'bg-amber-50/60 border-amber-200'
                      : 'bg-emerald-50/60 border-emerald-200'
                  }`}
                >
                  <p className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    {r.nutrient.replace('_', ' ')}
                  </p>
                  <p className="text-2xl font-extrabold mt-2 text-slate-900">{r.risk_percentage}%</p>
                  <span
                    className={`inline-block mt-3 text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full ${
                      isHigh
                        ? 'bg-rose-100 text-rose-700'
                        : isMod
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-emerald-100 text-emerald-700'
                    }`}
                  >
                    {r.risk_level} risk
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-10 border-2 border-dashed border-slate-100 rounded-xl">
            <p className="text-sm font-medium text-slate-500">No prediction record found.</p>
            <p className="text-xs text-slate-400 mt-1">Navigate to AI Analysis to run your first model evaluation.</p>
          </div>
        )}
      </div>
    </div>
  );
}