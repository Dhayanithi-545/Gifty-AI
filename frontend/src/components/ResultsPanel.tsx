import { Download, FileText, Copy } from 'lucide-react';
import type { ContactResult, RecommendedGift } from '../types/api';
import ContactCard from './ContactCard';

interface ResultsPanelProps {
  results: ContactResult[];
  processingContacts: Record<string, boolean>;
  onReviewAction: (contactName: string, action: 'approve' | 'reject' | 'edit' | 'regenerate', gift?: RecommendedGift, editedMessage?: string) => void;
  onExportPDF: () => void;
  onExportJSON: () => void;
  onCopyToClipboard: () => void;
}

export default function ResultsPanel({
  results,
  processingContacts,
  onReviewAction,
  onExportPDF,
  onExportJSON,
  onCopyToClipboard,
}: ResultsPanelProps) {
  if (results.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200/50 h-full flex flex-col justify-center items-center">
        <div className="text-center py-20 flex flex-col items-center justify-center">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 mb-4 shadow-inner">
            <FileText className="w-7 h-7" />
          </div>
          <h3 className="text-lg font-bold text-slate-700 font-display">No Recommendations Yet</h3>
          <p className="text-slate-400 text-sm max-w-sm mt-1">
            Load a sample contact payload or paste a custom JSON on the left, then click run.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-6 shadow-sm border border-slate-200/50 h-full flex flex-col overflow-hidden">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-5 pb-4 border-b border-slate-200/40 shrink-0">
        <h2 className="text-xl font-bold text-slate-900 font-display">
          Recommendations ({results.length} contact{results.length !== 1 ? 's' : ''})
        </h2>
        <div className="flex gap-2">
          <button
            onClick={onCopyToClipboard}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200/80 rounded-xl transition-all cursor-pointer"
          >
            <Copy className="w-3.5 h-3.5" />
            <span>Copy</span>
          </button>
          <button
            onClick={onExportJSON}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200/80 rounded-xl transition-all cursor-pointer"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>JSON</span>
          </button>
         
        </div>
      </div>

      <div className="flex-1 min-h-0 overflow-hidden">
        {/* Contact breakdown cards */}
        <div className="h-full overflow-y-auto pr-1 space-y-4 pb-4">
          {results.map((result) => (
            <ContactCard
              key={result.contact_name}
              result={result}
              isProcessing={processingContacts[result.contact_name] || false}
              onReviewAction={onReviewAction}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
