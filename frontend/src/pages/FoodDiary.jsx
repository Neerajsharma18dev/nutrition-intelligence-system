import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { Plus, Trash2, Calendar, Utensils } from 'lucide-react';

export default function FoodDiary() {
  // Default to today in YYYY-MM-DD format
  const [selectedDate, setSelectedDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [diary, setDiary] = useState({ entries: [], totals: {} });
  const [foods, setFoods] = useState([]);
  const [selectedFoodId, setSelectedFoodId] = useState(1);
  const [quantity, setQuantity] = useState(1.0);
  const [mealType, setMealType] = useState('breakfast');
  const [loading, setLoading] = useState(false);

  // Fetch diary entries for the chosen date
  const fetchDiary = async (targetDate = selectedDate) => {
    try {
      const res = await api.get(`/food-diary?entry_date=${targetDate}`);
      setDiary(res.data);
    } catch (err) {
      console.error('Failed to fetch diary entries:', err);
    }
  };

  const fetchFoods = async (q = '') => {
    try {
      const res = await api.get(`/foods/search?q=${q}`);
      setFoods(res.data);
      if (res.data.length > 0 && !selectedFoodId) {
        setSelectedFoodId(res.data[0].id);
      }
    } catch (err) {
      console.error('Failed to fetch food list:', err);
    }
  };

  // Re-fetch diary whenever selected date changes
  useEffect(() => {
    fetchDiary(selectedDate);
  }, [selectedDate]);

  useEffect(() => {
    fetchFoods();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post('/food-diary', {
        food_id: selectedFoodId,
        quantity: parseFloat(quantity),
        meal_type: mealType,
        entry_date: selectedDate, // Selected date sent to backend
      });
      await fetchDiary(selectedDate);
    } catch (err) {
      console.error('Failed to log meal:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/food-diary/${id}`);
      await fetchDiary(selectedDate);
    } catch (err) {
      console.error('Failed to delete entry:', err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header with Date Selection Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Food Diary & Nutrition Intake</h1>
          <p className="text-sm text-slate-500">Track daily logged foods and calculated micronutrient totals</p>
        </div>

        {/* Date Selector */}
        <div className="flex items-center gap-2 bg-white px-3 py-1.5 border border-slate-200 rounded-xl shadow-sm">
          <Calendar className="w-4 h-4 text-emerald-600 shrink-0" />
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="text-sm font-semibold text-slate-700 bg-transparent outline-none cursor-pointer"
          />
        </div>
      </div>

      {/* Add Entry Card */}
      <form onSubmit={handleAdd} className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
        <h2 className="text-sm font-bold text-slate-800 mb-3 flex items-center gap-2">
          <Utensils className="w-4 h-4 text-emerald-600" />
          <span>Log Food Consumption ({selectedDate})</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Select Food Item</label>
            <select
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={selectedFoodId}
              onChange={(e) => setSelectedFoodId(parseInt(e.target.value))}
            >
              {foods.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.name} ({f.serving_description})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Servings</label>
            <input
              type="number"
              step="0.5"
              min="0.5"
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1">Meal Slot</label>
            <select
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm"
              value={mealType}
              onChange={(e) => setMealType(e.target.value)}
            >
              <option value="breakfast">Breakfast</option>
              <option value="lunch">Lunch</option>
              <option value="dinner">Dinner</option>
              <option value="snack">Snack</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 bg-emerald-600 text-white rounded-lg text-sm font-semibold hover:bg-emerald-700 transition flex items-center justify-center gap-1.5 disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              <span>{loading ? 'Adding...' : 'Add Item'}</span>
            </button>
          </div>
        </div>
      </form>

      {/* Summary Chips */}
      {diary.totals && (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          {Object.entries(diary.totals).map(([k, v]) => (
            <div key={k} className="bg-white border border-slate-200 p-3 rounded-xl text-center shadow-sm">
              <p className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                {k.replace('_', ' ')}
              </p>
              <p className="text-base font-extrabold text-slate-800 mt-0.5">{v}</p>
            </div>
          ))}
        </div>
      )}

      {/* Entries List */}
      <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">
        <h2 className="text-sm font-bold text-slate-800 mb-3">Logged Items for {selectedDate}</h2>
        {diary.entries.length === 0 ? (
          <p className="text-xs text-slate-400 py-6 text-center">No foods logged for this date yet.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {diary.entries.map((entry) => (
              <div key={entry.id} className="py-3 flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-800">{entry.food.name}</p>
                  <p className="text-xs text-slate-400 capitalize">
                    {entry.meal_type} · {entry.quantity} serving ({entry.food.serving_description})
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-xs font-semibold text-slate-600">
                    {Math.round(entry.food.calories * entry.quantity)} kcal
                  </span>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 rounded-md transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
} 