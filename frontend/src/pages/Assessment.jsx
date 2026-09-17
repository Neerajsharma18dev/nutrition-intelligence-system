import React, { useState } from 'react';
import api from '../api/client';
import { Stethoscope, CheckCircle2, Save } from 'lucide-react';

const SYMPTOM_LIST = [
  { key: 'fatigue', label: 'Fatigue / Low Energy' },
  { key: 'hair_loss', label: 'Hair Loss' },
  { key: 'skin_problems', label: 'Dry / Problem Skin' },
  { key: 'muscle_weakness', label: 'Muscle Weakness' },
  { key: 'mood_changes', label: 'Mood Changes / Irritability' },
  { key: 'brittle_nails', label: 'Brittle Nails' },
  { key: 'pale_skin', label: 'Pale Skin' },
  { key: 'frequent_infections', label: 'Frequent Infections' },
  { key: 'poor_concentration', label: 'Brain Fog / Poor Focus' },
  { key: 'bone_joint_pain', label: 'Bone / Joint Aches' },
  { key: 'numbness_tingling', label: 'Numbness / Tingling' },
  { key: 'bleeding_gums', label: 'Bleeding Gums' },
];

export default function Assessment() {
  const [symptoms, setSymptoms] = useState(
    SYMPTOM_LIST.reduce((acc, curr) => ({ ...acc, [curr.key]: 0 }), {})
  );
  const [labs, setLabs] = useState({
    hemoglobin_g_dl: '',
    vitamin_d_ng_ml: '',
    vitamin_b12_pg_ml: '',
    ferritin_ng_ml: '',
    calcium_mg_dl: '',
  });
  const [msg, setMsg] = useState('');

  const handleSaveSymptoms = async (e) => {
    e.preventDefault();
    await api.post('/symptoms', symptoms);
    setMsg('Symptoms recorded successfully.');
    setTimeout(() => setMsg(''), 3000);
  };

  const handleSaveLabs = async (e) => {
    e.preventDefault();
    const payload = {};
    Object.entries(labs).forEach(([k, v]) => {
      payload[k] = v === '' ? null : parseFloat(v);
    });
    await api.post('/blood-tests', payload);
    setMsg('Blood laboratory values saved.');
    setTimeout(() => setMsg(''), 3000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Clinical Screening Inputs</h1>
        <p className="text-sm text-slate-500">Provide non-specific symptom severity and available lab results</p>
      </div>

      {msg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{msg}</span>
        </div>
      )}

      {/* Symptoms Section */}
      <form onSubmit={handleSaveSymptoms} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-800 mb-1">12-Point Symptom Assessment</h2>
        <p className="text-xs text-slate-400 mb-5">Rate severity over the past 30 days: 0 (None) to 3 (Severe)</p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {SYMPTOM_LIST.map((item) => (
            <div key={item.key} className="p-3 bg-slate-50/70 border border-slate-200 rounded-xl">
              <label className="block text-xs font-semibold text-slate-700 mb-2">{item.label}</label>
              <div className="grid grid-cols-4 gap-1">
                {[0, 1, 2, 3].map((val) => (
                  <button
                    type="button"
                    key={val}
                    onClick={() => setSymptoms({ ...symptoms, [item.key]: val })}
                    className={`py-1 text-xs font-bold rounded-lg transition ${
                      symptoms[item.key] === val
                        ? 'bg-emerald-600 text-white'
                        : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    {val}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <button
          type="submit"
          className="mt-5 px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition flex items-center gap-2 shadow-sm"
        >
          <Save className="w-4 h-4" />
          <span>Submit Symptoms</span>
        </button>
      </form>

      {/* Lab Results Section */}
      <form onSubmit={handleSaveLabs} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
        <h2 className="text-base font-bold text-slate-800 mb-1">Laboratory Blood Panel (Optional)</h2>
        <p className="text-xs text-slate-400 mb-5">
          Leave blank if not tested. The pipeline uses median imputation + missingness indicator flags.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Hemoglobin (g/dL)</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 13.5"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={labs.hemoglobin_g_dl}
              onChange={(e) => setLabs({ ...labs, hemoglobin_g_dl: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Vitamin D (ng/mL)</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 28.0"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={labs.vitamin_d_ng_ml}
              onChange={(e) => setLabs({ ...labs, vitamin_d_ng_ml: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Vitamin B12 (pg/mL)</label>
            <input
              type="number"
              step="1"
              placeholder="e.g. 350"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={labs.vitamin_b12_pg_ml}
              onChange={(e) => setLabs({ ...labs, vitamin_b12_pg_ml: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Ferritin (ng/mL)</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 45.0"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={labs.ferritin_ng_ml}
              onChange={(e) => setLabs({ ...labs, ferritin_ng_ml: e.target.value })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Calcium (mg/dL)</label>
            <input
              type="number"
              step="0.1"
              placeholder="e.g. 9.2"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={labs.calcium_mg_dl}
              onChange={(e) => setLabs({ ...labs, calcium_mg_dl: e.target.value })}
            />
          </div>
        </div>

        <button
          type="submit"
          className="mt-5 px-5 py-2.5 bg-slate-800 text-white rounded-xl text-sm font-semibold hover:bg-slate-900 transition flex items-center gap-2 shadow-sm"
        >
          <Save className="w-4 h-4" />
          <span>Save Blood Values</span>
        </button>
      </form>
    </div>
  );
}