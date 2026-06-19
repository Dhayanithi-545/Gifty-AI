import { useState, useEffect } from 'react';
import Header from './components/Header';
import InputPanel from './components/InputPanel';
import ResultsPanel from './components/ResultsPanel';
import giftAPI from './hooks/useGiftyAPI';
import type { ContactResult, ContactInput, RecommendedGift, SavedProfile } from './types/api';

function App() {
  const [currentPage, setCurrentPage] = useState<'home' | 'saved' | 'history'>('home');
  const [inputJson, setInputJson] = useState('');
  const [results, setResults] = useState<ContactResult[]>([]);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedProfiles, setSavedProfiles] = useState<SavedProfile[]>([]);
  const [apiHealth, setApiHealth] = useState<{ status: string; groq_key_configured: boolean; serper_key_configured: boolean } | null>(null);
  const [processingContacts, setProcessingContacts] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadSavedProfiles();
    checkAPIHealth();
  }, []);

  const loadSavedProfiles = () => {
    const saved = localStorage.getItem('gifty_profiles');
    if (saved) {
      setSavedProfiles(JSON.parse(saved));
    }
  };

  const checkAPIHealth = async () => {
    try {
      const health = await giftAPI.health();
      setApiHealth(health);
    } catch (e) {
      setApiHealth({ status: 'error', groq_key_configured: false, serper_key_configured: false });
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    setError(null);
    try {
      const data = JSON.parse(inputJson);
      const response = await giftAPI.runPipeline(data);
      setResults(response.results);
    } catch (e: any) {
      let errorMessage = 'Failed to process request';
      if (e.response?.data) {
        if (typeof e.response.data === 'string') {
          errorMessage = e.response.data;
        } else if (e.response.data.detail) {
          errorMessage = e.response.data.detail;
        } else if (Array.isArray(e.response.data)) {
          errorMessage = e.response.data.map((err: any) => err.msg).join(', ');
        } else {
          errorMessage = JSON.stringify(e.response.data);
        }
      } else if (e.message) {
        errorMessage = e.message;
      }
      setError(errorMessage);
    } finally {
      setProcessing(false);
    }
  };

  const handleSaveProfile = () => {
    try {
      const data = JSON.parse(inputJson);
      if (data.contacts && data.contacts.length > 0) {
        const contact = data.contacts[0];
        const profile: SavedProfile = {
          id: Date.now().toString(),
          name: contact.name,
          contact,
          createdAt: new Date().toISOString(),
        };
        const updated = [...savedProfiles, profile];
        setSavedProfiles(updated);
        localStorage.setItem('gifty_profiles', JSON.stringify(updated));
        alert('Profile saved!');
      }
    } catch (e) {
      alert('Invalid JSON format');
    }
  };

  const handleLoadProfile = (contact: ContactInput) => {
    setInputJson(JSON.stringify({ contacts: [contact] }, null, 2));
  };

  const handleReviewAction = async (
    contactName: string,
    action: 'approve' | 'reject' | 'edit' | 'regenerate',
    gift?: RecommendedGift,
    editedMessage?: string
  ) => {
    setProcessingContacts(prev => ({ ...prev, [contactName]: true }));
    try {
      const updated = await giftAPI.reviewAction({
        contact_name: contactName,
        action,
        edited_gift: gift,
        reviewer_note: editedMessage,
      });
      setResults(prev => prev.map(r => r.contact_name === contactName ? updated : r));
    } catch (e: any) {
      let errorMessage = 'Failed to perform action';
      if (e.response?.data) {
        if (typeof e.response.data === 'string') {
          errorMessage = e.response.data;
        } else if (e.response.data.detail) {
          errorMessage = e.response.data.detail;
        } else if (Array.isArray(e.response.data)) {
          errorMessage = e.response.data.map((err: any) => err.msg).join(', ');
        } else {
          errorMessage = JSON.stringify(e.response.data);
        }
      } else if (e.message) {
        errorMessage = e.message;
      }
      alert(errorMessage);
    } finally {
      setProcessingContacts(prev => ({ ...prev, [contactName]: false }));
    }
  };

  const handleExportJSON = () => {
    const data = JSON.stringify(results, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'gifty-recommendations.json';
    a.click();
  };

  const handleCopyToClipboard = () => {
    const data = JSON.stringify(results, null, 2);
    navigator.clipboard.writeText(data);
    alert('Copied to clipboard!');
  };

  const handleExportPDF = () => {
    alert('PDF export coming soon!');
  };

  const handleDeleteProfile = (id: string) => {
    const updated = savedProfiles.filter(p => p.id !== id);
    setSavedProfiles(updated);
    localStorage.setItem('gifty_profiles', JSON.stringify(updated));
  };

  return (
    <div className="min-h-screen lg:h-screen lg:overflow-hidden flex flex-col">
      <Header currentPage={currentPage} onPageChange={setCurrentPage} apiHealth={apiHealth} />

      <main className="w-full px-6 py-6 flex-1 flex flex-col min-h-0 overflow-hidden">
        {apiHealth && apiHealth.status !== 'ok' && (
          <div className="mb-6 p-4 bg-rose-50/70 border border-rose-200/60 backdrop-blur rounded-2xl text-rose-700 text-sm font-semibold flex items-center gap-2 shadow-sm animate-fade-in shrink-0">
            <span className="text-base">⚠️</span>
            <span>Please start the backend server: <code className="bg-rose-100 px-1.5 py-0.5 rounded font-mono ml-1">uvicorn app.main:app --host 127.0.0.1 --port 8000</code></span>
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-rose-50/70 border border-rose-200/60 backdrop-blur rounded-2xl text-rose-700 text-sm font-semibold flex items-center gap-2 shadow-sm animate-fade-in shrink-0">
            <span className="text-base">⚠️</span>
            <span>{typeof error === 'string' ? error : JSON.stringify(error)}</span>
          </div>
        )}

        {currentPage === 'home' && (
          <div className="grid grid-cols-1 lg:grid-cols-[25%_75%] gap-6 flex-1 min-h-0 overflow-y-auto lg:overflow-hidden">
            <div className="lg:h-full lg:overflow-y-auto pb-4 pr-1">
              <InputPanel
                inputJson={inputJson}
                setInputJson={setInputJson}
                onProcess={handleProcess}
                processing={processing}
                onSaveProfile={handleSaveProfile}
                onLoadProfile={handleLoadProfile}
                savedProfiles={savedProfiles}
              />
            </div>
            <div className="lg:h-full lg:overflow-hidden pb-4 pr-1">
              <ResultsPanel
                results={results}
                processingContacts={processingContacts}
                onReviewAction={handleReviewAction}
                onExportPDF={handleExportPDF}
                onExportJSON={handleExportJSON}
                onCopyToClipboard={handleCopyToClipboard}
              />
            </div>
          </div>
        )}

        {currentPage === 'saved' && (
          <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200/50 flex-1 overflow-y-auto">
            <h2 className="text-xl font-bold text-slate-900 font-display mb-5 pb-3 border-b border-slate-200/40">Saved Profiles</h2>
            {savedProfiles.length === 0 ? (
              <p className="text-slate-400 py-10 text-center text-sm font-medium">No saved profiles yet.</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {savedProfiles.map((profile) => (
                  <div key={profile.id} className="flex items-center justify-between p-4.5 bg-white/60 border border-slate-200/40 rounded-2xl hover:bg-white hover:border-slate-200 transition-all duration-200 shadow-sm">
                    <div>
                      <h3 className="font-bold text-slate-800 font-display text-base">{profile.name}</h3>
                      <p className="text-xs font-semibold text-slate-500 mt-0.5">{profile.contact.role} at {profile.contact.company}</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => {
                          handleLoadProfile(profile.contact);
                          setCurrentPage('home');
                        }}
                        className="px-3.5 py-1.5 text-xs font-bold bg-brand-600 hover:bg-brand-700 text-white rounded-xl shadow-sm transition-all cursor-pointer"
                      >
                        Load
                      </button>
                      <button
                        onClick={() => handleDeleteProfile(profile.id)}
                        className="px-3.5 py-1.5 text-xs font-semibold bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-100/60 rounded-xl transition-all cursor-pointer"
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {currentPage === 'history' && (
          <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200/50 flex-1 overflow-y-auto">
            <h2 className="text-xl font-bold text-slate-900 font-display mb-4">History</h2>
            <p className="text-slate-400 text-sm font-medium">History feature coming soon!</p>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
