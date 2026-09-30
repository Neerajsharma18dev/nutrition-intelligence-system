import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { RefreshCw, ArrowLeftRight, AlertCircle, Sparkles } from 'lucide-react';

export default function MealPlan() {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [swappingSlot, setSwappingSlot] = useState(null);
  const [error, setError] = useState(null);
  const [activeDiet, setActiveDiet] = useState('all'); // all, veg, vegan, gf

  // Active 7-day meal plan fetch
  const fetchPlan = async () => {
    setError(null);
    try {
      const res = await api.get('/meal-plan');
      setPlan(res.data.plan);
      if (res.data.diet_preference) {
        setActiveDiet(res.data.diet_preference);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch meal plan.');
    }
  };

  useEffect(() => {
    fetchPlan();
  }, []);

  // Regenerate schedule conforming to selected dietary filter
  const handleRegenerate = async (dietType = activeDiet) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.post(`/meal-plan/regenerate?diet=${dietType}`);
      setPlan(res.data.plan);
      setActiveDiet(dietType);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to regenerate schedule.');
    } finally {
      setLoading(false);
    }
  };

  // Tab switch handler: auto-regenerates target meals for selected dietary type
  const handleDietChange = (dietType) => {
    setActiveDiet(dietType);
    handleRegenerate(dietType);
  };

  // Milestone 3: Single meal swap respecting the active dietary target
  const handleSwapMeal = async (dayNum, slot, item) => {
    setSwappingSlot(`${dayNum}-${slot}`);
    try {
      const res = await api.post('/meal-plan/swap-meal', {
        day: dayNum,
        meal_slot: slot,
        current_food_id: typeof item === 'object' ? item.id : null,
        current_food_name: typeof item === 'object' ? item.name : String(item),
        diet_preference: activeDiet,
      });

      if (res.data?.status === 'success' && res.data.replacement) {
        const replacement = res.data.replacement;
        setPlan((prev) =>
          prev.map((d) => {
            if (d.day !== dayNum) return d;
            const updatedMeals = {
              ...d.meals,
              [slot]: replacement,
            };
            const updatedCalories = Object.values(updatedMeals).reduce(
              (acc, curr) => acc + (curr?.calories || 0),
              0
            );
            return {
              ...d,
              meals: updatedMeals,
              daily_calories: updatedCalories,
            };
          })
        );
      }
    } catch (err) {
      console.error('Swap failed:', err.response?.data?.detail || err.message);
    } finally {
      setSwappingSlot(null);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-2">
      {/* Header & Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-emerald-600" />
            Personalised 7-Day Meal Schedule
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Automated balanced meal distribution conforming to profile restrictions
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Dietary Filter Tabs */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
            {[
              { id: 'all', label: 'All Items' },
              { id: 'veg', label: 'Vegetarian' },
              { id: 'vegan', label: 'Vegan' },
              { id: 'gf', label: 'Gluten-Free' },
            ].map((tab) => (
              <button
                key={tab.id}
                disabled={loading}
                onClick={() => handleDietChange(tab.id)}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition disabled:opacity-50 ${
                  activeDiet === tab.id
                    ? 'bg-white text-emerald-700 shadow-sm'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Regenerate Action Button */}
          <button
            onClick={() => handleRegenerate(activeDiet)}
            disabled={loading}
            className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs sm:text-sm font-semibold hover:bg-emerald-700 transition flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 shrink-0"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Rebuilding...' : 'Regenerate 7 Days'}</span>
          </button>
        </div>
      </div>

      {/* Academic Prototype Notice */}
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <p className="text-xs text-amber-900 leading-relaxed">
          <span className="font-bold uppercase tracking-wide">Academic Prototype Notice: </span>
          Meal allocations are generated using synthetic nutrient weights and clinical cutoff baselines. Not certified medical advice.
        </p>
      </div>

      {/* Error View */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 p-4 rounded-xl text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={fetchPlan} className="font-bold underline ml-4 hover:text-rose-800">
            Retry
          </button>
        </div>
      )}

      {/* Empty State */}
      {!plan || plan.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-8 text-center text-slate-400 text-sm">
          No meal schedule active. Click "Regenerate 7 Days" to generate your schedule.
        </div>
      ) : (
        /* 7-Day Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {plan.map((d) => (
            <div key={d.day} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-3">
              <div className="flex items-center justify-between border-b border-slate-100 pb-2">
                <span className="text-sm font-bold text-slate-800">Day {d.day}</span>
                <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                  {d.daily_calories} kcal
                </span>
              </div>

              <div className="space-y-2 text-xs">
                {Object.entries(d.meals).map(([slot, item]) => {
                  const isSwapping = swappingSlot === `${d.day}-${slot}`;
                  return (
                    <div key={slot} className="p-2.5 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-0.5">
                        <span>{slot}</span>
                        <span>{item.calories} kcal</span>
                      </div>
                      <p className="font-semibold text-slate-800 text-xs mt-0.5">{item.name}</p>
                      <p className="text-slate-400 text-[11px] mt-0.5">{item.serving}</p>

                      <div className="mt-2 flex justify-end">
                        <button
                          onClick={() => handleSwapMeal(d.day, slot, item)}
                          disabled={isSwapping}
                          className="text-[11px] text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1 disabled:opacity-50"
                        >
                          <ArrowLeftRight className={`w-3 h-3 ${isSwapping ? 'animate-spin' : ''}`} />
                          <span>{isSwapping ? 'Swapping...' : 'Swap'}</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 