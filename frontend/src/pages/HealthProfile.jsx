import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Save, CheckCircle2 } from 'lucide-react';

export default function HealthProfile() {
  const [form, setForm] = useState({
    age: 26,
    gender: 'female',
    height_cm: 168.0,
    weight_kg: 62.0,
    activity_level: 'moderate',
    sun_exposure_hours: 1.5,
    medical_conditions: [],
    dietary_restrictions: ['vegetarian'],
    health_goals: ['increase_energy'],
  });
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/profile').then((res) => {
      if (res.data) setForm(res.data);
    }).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSaved(false);
    try {
      await api.put('/profile', form);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save health profile.');
    }
  };

  const toggleRestriction = (item) => {
    setForm((prev) => {
      const exists = prev.dietary_restrictions.includes(item);
      return {
        ...prev,
        dietary_restrictions: exists
          ? prev.dietary_restrictions.filter((r) => r !== item)
          : [...prev.dietary_restrictions, item],
      };
    });
  };

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Patient Health Profile</h1>
        <p className="text-sm text-slate-500">Demographic baselines and dietary restrictions</p>
      </div>

      {saved && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xl text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>Health profile saved successfully.</span>
        </div>
      )}

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-xs">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-5">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Age</label>
            <input
              type="number"
              min="1"
              max="120"
              required
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: parseInt(e.target.value) || 0 })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Biological Gender</label>
            <select
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={form.gender}
              onChange={(e) => setForm({ ...form, gender: e.target.value })}
            >
              <option value="female">Female</option>
              <option value="male">Male</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Height (cm)</label>
            <input
              type="number"
              step="0.1"
              required
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={form.height_cm}
              onChange={(e) => setForm({ ...form, height_cm: parseFloat(e.target.value) || 0 })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Weight (kg)</label>
            <input
              type="number"
              step="0.1"
              required
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={form.weight_kg}
              onChange={(e) => setForm({ ...form, weight_kg: parseFloat(e.target.value) || 0 })}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Activity Level</label>
            <select
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={form.activity_level}
              onChange={(e) => setForm({ ...form, activity_level: e.target.value })}
            >
              <option value="sedentary">Sedentary (desk job, low exercise)</option>
              <option value="light">Light (1-3 days exercise)</option>
              <option value="moderate">Moderate (3-5 days exercise)</option>
              <option value="active">Active (6-7 days intense)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Daily Sun Exposure (Hours)</label>
            <input
              type="number"
              step="0.5"
              min="0"
              max="24"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={form.sun_exposure_hours}
              onChange={(e) => setForm({ ...form, sun_exposure_hours: parseFloat(e.target.value) || 0 })}
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-2">Dietary Restrictions</label>
          <div className="flex flex-wrap gap-2">
            {['vegetarian', 'vegan', 'gluten_free', 'dairy_free'].map((r) => {
              const active = form.dietary_restrictions.includes(r);
              return (
                <button
                  type="button"
                  key={r}
                  onClick={() => toggleRestriction(r)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                    active
                      ? 'bg-emerald-600 text-white border-emerald-600'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  {r.replace('_', ' ').toUpperCase()}
                </button>
              );
            })}
          </div>
        </div>

        <button
          type="submit"
          className="px-5 py-2.5 bg-emerald-600 text-white rounded-xl text-sm font-semibold hover:bg-emerald-700 transition flex items-center gap-2 shadow-sm"
        >
          <Save className="w-4 h-4" />
          <span>Save Profile</span>
        </button>
      </form>
    </div>
  );
}