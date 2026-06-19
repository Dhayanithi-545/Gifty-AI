import { useState } from 'react';
import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';
import type { ContactResult, RecommendedGift } from '../types/api';
import GiftCard from './GiftCard';

interface ContactCardProps {
  result: ContactResult;
  onReviewAction: (contactName: string, action: 'approve' | 'reject' | 'edit' | 'regenerate', gift?: RecommendedGift, editedMessage?: string) => void;
}

export default function ContactCard({ result, onReviewAction }: ContactCardProps) {
  const [expanded, setExpanded] = useState(true);
  const [activeTab, setActiveTab] = useState<'recommendations' | 'signals' | 'search' | 'trace'>('recommendations');
  const [editingGift, setEditingGift] = useState<number | null>(null);
  const [editedMessages, setEditedMessages] = useState<Record<number, string>>({});

  const handleEditGift = (gift: RecommendedGift) => {
    setEditingGift(gift.rank);
    setEditedMessages(prev => ({ ...prev, [gift.rank]: gift.personalised_message }));
  };

  const handleSaveEdit = (gift: RecommendedGift) => {
    onReviewAction(result.contact_name, 'edit', { ...gift, personalised_message: editedMessages[gift.rank] }, editedMessages[gift.rank]);
    setEditingGift(null);
  };

  const handleCancelEdit = () => {
    setEditingGift(null);
  };

  return (
    <div className="bg-white/90 border border-slate-200/60 rounded-2xl shadow-sm mb-5 overflow-hidden transition-all duration-300 hover:shadow-md">
      <div
        className="flex items-center justify-between p-4.5 cursor-pointer hover:bg-slate-50/50 transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3.5">
          <div className="flex items-center justify-center w-11 h-11 bg-brand-50 border border-brand-100 rounded-2xl shadow-sm">
            <span className="text-brand-600 font-extrabold font-display text-lg">{result.contact_name.charAt(0)}</span>
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-800 font-display">{result.contact_name}</h3>
            <div className="flex items-center gap-3 text-xs font-medium text-slate-500 mt-0.5">
              <span className="px-2 py-0.5 bg-slate-100 rounded-md">{result.recommended_gifts.length} recommended</span>
              {result.warnings.length > 0 && (
                <span className="flex items-center gap-1 text-amber-600 bg-amber-50 px-2 py-0.5 rounded-md">
                  <AlertCircle className="w-3.5 h-3.5" />
                  {result.warnings.length} warning(s)
                </span>
              )}
            </div>
          </div>
        </div>
        {expanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
      </div>

      {expanded && (
        <div className="border-t border-slate-200/50">
          <div className="flex border-b border-slate-200/40 bg-white/95 backdrop-blur-sm px-3 sticky top-0 z-10">
            <button
              onClick={() => setActiveTab('recommendations')}
              className={`px-4 py-3 text-sm font-semibold transition-all relative cursor-pointer ${activeTab === 'recommendations'
                  ? 'text-brand-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-brand-600'
                  : 'text-slate-500 hover:text-slate-900'
                }`}
            >
              Recommendations
            </button>
            <button
              onClick={() => setActiveTab('signals')}
              className={`px-4 py-3 text-sm font-semibold transition-all relative cursor-pointer ${activeTab === 'signals'
                  ? 'text-brand-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-brand-600'
                  : 'text-slate-500 hover:text-slate-900'
                }`}
            >
              Signals
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`px-4 py-3 text-sm font-semibold transition-all relative cursor-pointer ${activeTab === 'search'
                  ? 'text-brand-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-brand-600'
                  : 'text-slate-500 hover:text-slate-900'
                }`}
            >
              Search
            </button>
            <button
              onClick={() => setActiveTab('trace')}
              className={`px-4 py-3 text-sm font-semibold transition-all relative cursor-pointer ${activeTab === 'trace'
                  ? 'text-brand-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-brand-600'
                  : 'text-slate-500 hover:text-slate-900'
                }`}
            >
              Trace
            </button>
          </div>

          <div className="p-5">
            {activeTab === 'recommendations' && (
              <div className="space-y-4">
                {result.recommended_gifts.length === 0 ? (
                  <p className="text-slate-400 text-center py-10 text-sm">No gifts recommended</p>
                ) : (
                  result.recommended_gifts.map((gift) => (
                    <div key={gift.rank} id={`gift-card-${result.contact_name}-${gift.rank}`}>
                      <GiftCard
                        gift={gift}
                        onApprove={() => onReviewAction(result.contact_name, 'approve')}
                        onReject={() => onReviewAction(result.contact_name, 'reject')}
                        onEdit={() => handleEditGift(gift)}
                        onRegenerate={() => onReviewAction(result.contact_name, 'regenerate')}
                        isEditing={editingGift === gift.rank}
                        editedMessage={editedMessages[gift.rank] || ''}
                        onMessageChange={(value) => setEditedMessages(prev => ({ ...prev, [gift.rank]: value }))}
                        onSaveEdit={() => handleSaveEdit(gift)}
                        onCancelEdit={handleCancelEdit}
                      />
                    </div>
                  ))
                )}
              </div>
            )}

            {activeTab === 'signals' && (
              <div className="space-y-5">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">Strong Signals</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.profile_signals.strong_signals.map((signal, idx) => (
                      <span key={idx} className="px-3.5 py-1 bg-brand-50 border border-brand-100 text-brand-700 rounded-xl text-sm font-medium">
                        {signal}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">Weak Signals</h4>
                  <div className="flex flex-wrap gap-2">
                    {result.profile_signals.weak_signals.map((signal, idx) => (
                      <span key={idx} className="px-3.5 py-1 bg-slate-100 border border-slate-200/60 text-slate-600 rounded-xl text-sm font-medium">
                        {signal}
                      </span>
                    ))}
                  </div>
                </div>
                {result.profile_signals.signals_to_avoid.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5 text-rose-500">Signals to Avoid</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.profile_signals.signals_to_avoid.map((signal, idx) => (
                        <span key={idx} className="px-3.5 py-1 bg-rose-50 border border-rose-100 text-rose-700 rounded-xl text-sm font-medium">
                          {signal}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'search' && (
              <div className="space-y-5">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">Search Queries</h4>
                  <ul className="space-y-2">
                    {result.search_trace.queries_used.map((query, idx) => (
                      <li key={idx} className="text-sm text-slate-600 bg-slate-50 border border-slate-200/30 px-3.5 py-2 rounded-xl font-medium">
                        🔍 "{query}"
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-slate-50/50 border border-slate-200/40 p-4 rounded-xl">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Provider</h4>
                    <p className="text-sm font-bold text-slate-700 capitalize">{result.search_trace.provider_used}</p>
                  </div>
                  <div className="bg-slate-50/50 border border-slate-200/40 p-4 rounded-xl">
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Products Considered</h4>
                    <p className="text-sm font-bold text-slate-700">{result.search_trace.products_considered_count}</p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'trace' && (
              <div className="space-y-5">
                <div>
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5">Guardrail Report</h4>
                  <div className="bg-slate-50/50 border border-slate-200/40 p-4 rounded-xl space-y-2">
                    <p className="text-sm font-medium text-slate-600">
                      Status: <span className={`font-bold ${result.guardrail_report.passed ? 'text-emerald-600' : 'text-rose-600'}`}>{result.guardrail_report.passed ? 'Passed' : 'Flags Triggered'}</span>
                    </p>
                    {result.guardrail_report.blocked_terms_found.length > 0 && (
                      <p className="text-sm text-slate-600">
                        Blocked: <span className="font-mono text-xs bg-rose-50 border border-rose-100 text-rose-700 px-1.5 py-0.5 rounded">{result.guardrail_report.blocked_terms_found.join(', ')}</span>
                      </p>
                    )}
                    {result.guardrail_report.signals_removed.length > 0 && (
                      <p className="text-sm text-slate-600">
                        Removed Signals: <span className="font-mono text-xs bg-amber-50 border border-amber-100 text-amber-700 px-1.5 py-0.5 rounded">{result.guardrail_report.signals_removed.join(', ')}</span>
                      </p>
                    )}
                  </div>
                </div>
                {result.warnings.length > 0 && (
                  <div>
                    <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2.5 text-amber-500">Warnings</h4>
                    <div className="space-y-2">
                      {result.warnings.map((warning, idx) => (
                        <p key={idx} className="text-sm text-amber-700 bg-amber-50/50 border border-amber-200/40 px-3.5 py-2 rounded-xl">
                          ⚠ {warning}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
                <div className="bg-slate-50/50 border border-slate-200/40 p-4 rounded-xl">
                  <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Review Status</h4>
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${result.human_review.status === 'approved' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
                      result.human_review.status === 'rejected' ? 'bg-rose-100 text-rose-800 border border-rose-200' :
                        'bg-amber-100 text-amber-800 border border-amber-200'
                    }`}>
                    {result.human_review.status}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}