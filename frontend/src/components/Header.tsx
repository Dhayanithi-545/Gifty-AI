import { Gift, Users, History } from 'lucide-react';

interface HeaderProps {
  currentPage: 'home' | 'saved' | 'history';
  onPageChange: (page: 'home' | 'saved' | 'history') => void;
  apiHealth: { status: string; groq_key_configured: boolean; serper_key_configured: boolean } | null;
}

export default function Header({ currentPage, onPageChange, apiHealth }: HeaderProps) {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-slate-200/50 sticky top-0 z-50 shadow-sm w-full font-display">
      <div className="w-full px-6">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center gap-3">
            <div className="p-1.5 bg-gradient-to-tr from-brand-600 to-indigo-500 rounded-xl text-white shadow-md shadow-brand-500/20">
              <Gift className="w-5 h-5" />
            </div>
            <h1 className="text-xl playwrite-nz-basic-guides-regular bg-gradient-to-r from-brand-600 to-indigo-600 bg-clip-text text-transparent tracking-wide select-none py-1">
              Gifty
            </h1>
          </div>

          {/* API Health / Provider Configured indicators */}
          {apiHealth && (
            <div className="flex items-center gap-2 md:gap-4 bg-slate-50/80 border border-slate-200/40 rounded-xl px-2.5 md:px-4 py-1.5 text-[10px] md:text-xs">
              <div className="flex items-center gap-1.5">
                <span className={`w-2 h-2 rounded-full ${apiHealth.status === 'ok' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
                <span className="hidden sm:inline font-bold text-slate-700">API:</span>
                <span className={`font-extrabold ${apiHealth.status === 'ok' ? 'text-emerald-600' : 'text-rose-600'}`}>
                  {apiHealth.status === 'ok' ? 'OK' : 'Err'}
                </span>
              </div>
              <span className="w-px h-3 bg-slate-300" />
              <div className="flex items-center gap-1">
                <span className="text-slate-400 font-bold uppercase tracking-wider text-[9px] md:text-[10px]">Groq:</span>
                <span className={`font-bold ${apiHealth.groq_key_configured ? 'text-emerald-600' : 'text-rose-500'}`}>
                  {apiHealth.groq_key_configured ? '✓' : '✗'}
                </span>
              </div>
              <span className="w-px h-3 bg-slate-300" />
              <div className="flex items-center gap-1">
                <span className="text-slate-400 font-bold uppercase tracking-wider text-[9px] md:text-[10px]">Serper:</span>
                <span className={`font-bold ${apiHealth.serper_key_configured ? 'text-emerald-600' : 'text-rose-500'}`}>
                  {apiHealth.serper_key_configured ? '✓' : '✗'}
                </span>
              </div>
            </div>
          )}

          <nav className="flex gap-2">
            <button
              onClick={() => onPageChange('home')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 cursor-pointer ${
                currentPage === 'home'
                  ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/25'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Gift className="w-4 h-4" />
              <span>Home</span>
            </button>
            <button
              onClick={() => onPageChange('saved')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 cursor-pointer ${
                currentPage === 'saved'
                  ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/25'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Saved Profiles</span>
            </button>
            <button
              onClick={() => onPageChange('history')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 cursor-pointer ${
                currentPage === 'history'
                  ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/25'
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
              }`}
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
}
