import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Shell from './components/layout/Shell';
import Auth from './pages/Auth';
import Dashboard from './pages/Dashboard';
import HealthProfile from './pages/HealthProfile';
import FoodDiary from './pages/FoodDiary';
import Assessment from './pages/Assessment';
import AIAnalysis from './pages/AIAnalysis';
import Recommendations from './pages/Recommendations';
import MealPlan from './pages/MealPlan';

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-xs text-slate-400 font-semibold tracking-wider uppercase">
        Loading System Engine...
      </div>
    );
  }

  return user ? children : <Navigate to="/auth" replace />;
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/auth" element={<Auth />} />

          {/* Protected Application Frame */}
          <Route
            element={
              <ProtectedRoute>
                <Shell />
              </ProtectedRoute>
            }
          >
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<HealthProfile />} />
            <Route path="/diary" element={<FoodDiary />} />
            <Route path="/assessment" element={<Assessment />} />
            <Route path="/analysis" element={<AIAnalysis />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/meal-plan" element={<MealPlan />} />
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}