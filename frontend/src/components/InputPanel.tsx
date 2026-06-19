import { useState } from 'react';
import { Play, Save } from 'lucide-react';
import { sampleContact, sampleBulkContacts } from '../utils/sampleData';
import type { ContactInput } from '../types/api';

interface InputPanelProps {
  inputJson: string;
  setInputJson: (value: string) => void;
  onProcess: () => void;
  processing: boolean;
  onSaveProfile: () => void;
  onLoadProfile: (profile: ContactInput) => void;
  savedProfiles: Array<{ id: string; name: string; contact: ContactInput }>;
}

export default function InputPanel({
  inputJson,
  setInputJson,
  onProcess,
  processing,
  onSaveProfile,
  onLoadProfile,
  savedProfiles,
}: InputPanelProps) {
  const [jsonError, setJsonError] = useState<string | null>(null);

  const handleJsonChange = (value: string) => {
    setInputJson(value);
    try {
      if (value.trim()) {
        const parsed = JSON.parse(value);
        // Auto-wrap if it's just an array
        if (Array.isArray(parsed)) {
          const wrapped = { contacts: parsed };
          setInputJson(JSON.stringify(wrapped, null, 2));
          setJsonError(null);
        }
        // Validate that it has the correct structure
        else if (!parsed.contacts || !Array.isArray(parsed.contacts)) {
          setJsonError('JSON must have a "contacts" array');
        } else {
          setJsonError(null);
        }
      } else {
        setJsonError(null);
      }
    } catch (e) {
      setJsonError('Invalid JSON format');
    }
  };

  const loadSample = (bulk: boolean = false) => {
    const data = bulk ? { contacts: sampleBulkContacts } : { contacts: [sampleContact] };
    setInputJson(JSON.stringify(data, null, 2));
    setJsonError(null);
  };

  const handleLoadProfile = (profile: ContactInput) => {
    onLoadProfile(profile);
    setInputJson(JSON.stringify({ contacts: [profile] }, null, 2));
    setJsonError(null);
  };

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200/50">
      <div className="flex justify-between items-center mb-5">
        <h2 className="text-xl font-bold text-slate-900 font-display">Input</h2>
        <div className="flex gap-2">
          <button
            onClick={() => loadSample(false)}
            className="px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200/80 rounded-xl transition-all cursor-pointer"
          >
            Sample (Single)
          </button>
          <button
            onClick={() => loadSample(true)}
            className="px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200/80 rounded-xl transition-all cursor-pointer"
          >
            Sample (Bulk)
          </button>
        </div>
      </div>

      {savedProfiles.length > 0 && (
        <div className="mb-5">
          <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
            Load Saved Profile
          </label>
          <select
            onChange={(e) => {
              const profile = savedProfiles.find(p => p.id === e.target.value);
              if (profile) handleLoadProfile(profile.contact);
            }}
            className="w-full px-4 py-2.5 border border-slate-200 bg-white/50 rounded-xl text-slate-700 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none transition-all cursor-pointer"
          >
            <option value="">Select a profile...</option>
            {savedProfiles.map((profile) => (
              <option key={profile.id} value={profile.id}>
                {profile.name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="mb-5">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
          Contact Payload (JSON)
        </label>
        <textarea
          value={inputJson}
          onChange={(e) => handleJsonChange(e.target.value)}
          placeholder='Paste your JSON here. Format: {"contacts": [{"name": "John Doe", ...}]}'
          className="w-full h-80 px-4 py-3 border border-slate-200 bg-white/50 rounded-2xl focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none font-mono text-sm resize-none transition-all"
        />
        {jsonError && (
          <p className="mt-2 text-sm text-red-600 flex items-center gap-1">
            <span>⚠</span> {jsonError}
          </p>
        )}
        <p className="mt-2.5 text-xs text-slate-400">
          Note: JSON must be wrapped in a "contacts" array. Use the load buttons above to see the correct schema.
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={onProcess}
          disabled={processing || !!jsonError || !inputJson.trim()}
          className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-xl disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed shadow-md hover:shadow-lg shadow-brand-500/10 hover:shadow-brand-500/20 transition-all duration-200 cursor-pointer"
        >
          <Play className="w-4 h-4 fill-current" />
          <span>{processing ? 'Processing...' : 'Run Recommendations'}</span>
        </button>
        <button
          onClick={onSaveProfile}
          disabled={!inputJson.trim() || !!jsonError}
          className="flex items-center justify-center gap-2 px-5 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl disabled:bg-slate-50 disabled:text-slate-300 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
        >
          <Save className="w-4 h-4" />
          <span>Save Profile</span>
        </button>
      </div>
    </div>
  );
}
