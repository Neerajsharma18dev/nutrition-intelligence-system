import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { ShieldAlert, Menu, X } from 'lucide-react';

export default function Shell() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-slate-50 overflow-hidden text-slate-800 antialiased font-sans">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex shrink-0 w-64 h-full border-r border-slate-200 bg-white z-20">
        <Sidebar />
      </div>

      {/* Mobile Drawer Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <div 
            className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative z-50 flex flex-col w-72 max-w-[80%] bg-white h-full shadow-2xl">
            <div className="p-4 flex justify-between items-center border-b border-slate-100">
              <span className="font-bold text-sm text-slate-900">Navigation</span>
              <button 
                onClick={() => setMobileMenuOpen(false)}
                className="p-1.5 rounded-lg text-slate-500 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              <Sidebar onNavigate={() => setMobileMenuOpen(false)} />
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        {/* Mobile Header Bar */}
        <header className="lg:hidden bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between shrink-0">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="p-2 rounded-xl text-slate-600 hover:bg-slate-100 focus:outline-none"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <span className="font-bold text-sm text-slate-900">Nutrition Intel</span>
          <div className="w-8" />
        </header>

        {/* Academic Disclaimer Header */}
        <div className="bg-amber-50 border-b border-amber-200/80 px-4 md:px-8 py-2.5 text-xs text-amber-800 flex flex-col sm:flex-row sm:items-center justify-between gap-2 shrink-0">
          <div className="flex items-center gap-2 font-medium">
            <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
            <span>Academic Research Prototype: Not intended for medical diagnosis or clinical prescription.</span>
          </div>
          <span className="self-start sm:self-auto text-[10px] font-bold tracking-wider uppercase text-amber-700 bg-amber-100/80 px-2 py-0.5 rounded">
            v0.1.0 Synthetic
          </span>
        </div>

        {/* Dynamic Body: Ab yeh pura available area utilize karega */}
        <main className="flex-1 overflow-y-auto px-4 py-6 md:px-8 md:py-8 lg:px-10">
          <div className="w-full space-y-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}