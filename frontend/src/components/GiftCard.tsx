import { ExternalLink, Check, X, Edit, RefreshCw } from 'lucide-react';
import type { RecommendedGift } from '../types/api';

interface GiftCardProps {
  gift: RecommendedGift;
  status?: string;
  onApprove: () => void;
  onReject: () => void;
  onEdit: () => void;
  onRegenerate: () => void;
  isEditing: boolean;
  editedMessage: string;
  onMessageChange: (value: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
}

export default function GiftCard({
  gift,
  status = 'pending_review',
  onApprove,
  onReject,
  onEdit,
  onRegenerate,
  isEditing,
  editedMessage,
  onMessageChange,
  onSaveEdit,
  onCancelEdit,
}: GiftCardProps) {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-emerald-50 border border-emerald-100 text-emerald-800';
      case 'medium': return 'bg-amber-50 border border-amber-100 text-amber-800';
      case 'high': return 'bg-rose-50 border border-rose-100 text-rose-800';
      default: return 'bg-slate-50 border border-slate-200 text-slate-800';
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.7) return 'bg-emerald-500';
    if (score >= 0.5) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getBorderColor = () => {
    switch (status) {
      case 'approved': return 'border-emerald-300 bg-emerald-50/5 shadow-emerald-50/10';
      case 'rejected': return 'border-rose-200 bg-rose-50/5 opacity-80 shadow-rose-50/5';
      case 'edited': return 'border-indigo-300 bg-indigo-50/5 shadow-indigo-50/10';
      default: return 'border-slate-200/50 hover:border-slate-200';
    }
  };

  return (
    <div className={`bg-slate-50/40 border rounded-2xl p-5 shadow-sm transition-all duration-300 ${getBorderColor()}`}>
      <div className="flex flex-col sm:flex-row justify-between sm:items-start gap-4 mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2.5">
            <span className="text-xs font-bold text-brand-600 bg-brand-50 border border-brand-100 px-2.5 py-1 rounded-lg">
              Rank #{gift.rank}
            </span>
            <span className={`text-xs font-semibold px-2.5 py-1 rounded-lg capitalize ${getRiskColor(gift.risk_level)}`}>
              {gift.risk_level} Risk
            </span>
          </div>
          <h3 className="text-lg font-bold text-slate-800 font-display mb-1">{gift.gift_name}</h3>
          <p className="text-sm font-medium text-slate-500 mb-2">
            {gift.store} • <span className="text-slate-800 font-bold">{gift.estimated_price}</span>
          </p>
          <a
            href={gift.product_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sm font-semibold text-brand-600 hover:text-brand-700 transition-colors"
          >
            View Product <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
        <div className="flex flex-col sm:items-end gap-2">
          <div className="sm:text-right">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Confidence</div>
            <div className="flex items-center gap-2.5">
              <div className="w-24 h-2.5 bg-slate-200/70 rounded-full overflow-hidden shadow-inner">
                <div
                  className={`h-full ${getConfidenceColor(gift.confidence_score)} transition-all duration-500`}
                  style={{ width: `${gift.confidence_score * 100}%` }}
                />
              </div>
              <span className="text-xs font-extrabold text-slate-700">{Math.round(gift.confidence_score * 100)}%</span>
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-4 mb-5 pb-4 border-b border-slate-200/50">
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Why this gift:</h4>
          <p className="text-sm text-slate-600 font-medium leading-relaxed">{gift.why_this_gift}</p>
        </div>
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Personalisation reasoning:</h4>
          <p className="text-sm text-slate-600 font-medium leading-relaxed">{gift.personalisation_reasoning}</p>
        </div>
        {gift.assumptions.length > 0 && (
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">Assumptions:</h4>
            <ul className="text-sm text-slate-600 font-medium list-disc list-inside space-y-0.5">
              {gift.assumptions.map((assumption, idx) => (
                <li key={idx} className="leading-relaxed">{assumption}</li>
              ))}
            </ul>
          </div>
        )}
        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1.5">Personalised message:</h4>
          {isEditing ? (
            <textarea
              value={editedMessage}
              onChange={(e) => onMessageChange(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-slate-200 bg-white rounded-xl text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none resize-none transition-all"
              rows={4}
            />
          ) : (
            <div className="text-sm text-slate-700 bg-white/70 border border-slate-200/30 p-3 rounded-xl whitespace-pre-wrap leading-relaxed font-medium italic">
              "{gift.personalised_message}"
            </div>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 pt-1">
        {isEditing ? (
          <>
            <button
              onClick={onSaveEdit}
              className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-xl transition-all text-sm shadow-sm cursor-pointer"
            >
              <Check className="w-4 h-4" /> Save
            </button>
            <button
              onClick={onCancelEdit}
              className="flex-1 flex items-center justify-center gap-1.5 px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl transition-all text-sm cursor-pointer"
            >
              <X className="w-4 h-4" /> Cancel
            </button>
          </>
        ) : (
          <>
            <button
              onClick={onApprove}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 font-semibold rounded-xl transition-all text-sm cursor-pointer ${
                status === 'approved'
                  ? 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm'
                  : status === 'rejected'
                  ? 'bg-slate-100 hover:bg-slate-200 text-slate-400 border border-slate-200/30 opacity-50'
                  : 'bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-100'
              }`}
            >
              <Check className="w-4 h-4" /> Approve
            </button>
            <button
              onClick={onReject}
              className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 font-semibold rounded-xl transition-all text-sm cursor-pointer ${
                status === 'rejected'
                  ? 'bg-rose-600 hover:bg-rose-700 text-white shadow-sm'
                  : status === 'approved'
                  ? 'bg-slate-100 hover:bg-slate-200 text-slate-400 border border-slate-200/30 opacity-50'
                  : 'bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-100'
              }`}
            >
              <X className="w-4 h-4" /> Reject
            </button>
            <button
              onClick={onEdit}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold rounded-xl transition-all text-sm cursor-pointer"
            >
              <Edit className="w-4 h-4" /> Edit
            </button>
            <button
              onClick={onRegenerate}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-brand-50 hover:bg-brand-100 border border-brand-100/60 text-brand-700 font-semibold rounded-xl transition-all text-sm cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" /> Regenerate
            </button>
          </>
        )}
      </div>
    </div>
  );
}
