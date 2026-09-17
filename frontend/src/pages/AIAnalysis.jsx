import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Cpu, RefreshCw, AlertCircle, CheckCircle2, TrendingUp, TrendingDown } from 'lucide-react';

export default function AIAnalysis() {
  const [prediction, setPrediction] = useState(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  const fetchLatest = async () => {
    try {
      const res = await api.get('/predict/latest');
      setPrediction(res.data);
    } catch {}
  };

  useEffect(() => {
    fetchLatest();
  }, []);

  const handleTriggerPrediction = async () => {
    setError('');
    setRunning(true);
    try {
      const res = await api.post('/predict');
      setPrediction(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Inference failed. Ensure Health Profile is filled.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Risk Screening & Explainability</h1>
          <p className="text-sm text-slate-500">Multi-target Random Forest classifier outputs with signed SHAP factor impact</p>
        </div>
        <button
          onClick={handleTriggerPrediction}
          disabled={running}
          className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${running ? 'animate-spin' : ''}`} />
          <span>{running ? 'Computing SHAP Tree...' : 'Execute ML Inference'}</span>
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {prediction && (
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Composite Nutrition Status</p>
              <p className="text-2xl font-extrabold text-slate-900 mt-0.5">{prediction.overall_score} / 100</p>
            </div>
            <span className="text-xs text-slate-400 font-medium">
              Evaluated on: {new Date(prediction.created_at).toLocaleString()}
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {prediction.results.map((r) => {
              const isHigh = r.risk_level === 'high';
              const isMod = r.risk_level === 'moderate';

              return (
                <div key={r.nutrient} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-base font-bold text-slate-800 uppercase tracking-wide">
                        {r.nutrient.replace('_', ' ')}
                      </h2>
                      <p className="text-xs text-slate-400">Confidence Metric: {Math.round(r.confidence * 100)}%</p>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-black text-slate-900">{r.risk_percentage}%</span>
                      <span
                        className={`block text-[10px] font-bold uppercase px-2 py-0.5 rounded mt-0.5 ${
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
                  </div>

                  {/* SHAP Factors */}
                  <div>
                    <p className="text-xs font-bold text-slate-600 mb-2">Key SHAP Decision Factors:</p>
                    <div className="space-y-1.5">
                      {r.top_factors.map((f, idx) => {
                        const increasesRisk = f.direction === 'increased_risk';
                        return (
                          <div
                            key={idx}
                            className="text-xs p-2 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-between"
                          >
                            <span className="text-slate-700 font-medium">{f.label}</span>
                            <span
                              className={`flex items-center gap-1 font-semibold text-[11px] ${
                                increasesRisk ? 'text-rose-600' : 'text-emerald-600'
                              }`}
                            >
                              {increasesRisk ? (
                                <>
                                  <TrendingUp className="w-3 h-3" /> Elevates Risk (+{f.impact.toFixed(2)})
                                </>
                              ) : (
                                <>
                                  <TrendingDown className="w-3 h-3" /> Mitigates Risk ({f.impact.toFixed(2)})
                                </>
                              )}
                            </span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}