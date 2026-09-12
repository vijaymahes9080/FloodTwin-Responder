import React from 'react';
import { ResponseBrief } from '../types';
import { FileText, ShieldAlert, CheckCircle2, Clock, BookOpen, AlertTriangle } from 'lucide-react';

interface BriefsViewProps {
  briefs: ResponseBrief[];
  onOpenApproval: (brief: ResponseBrief) => void;
}

export const BriefsView: React.FC<BriefsViewProps> = ({ briefs, onOpenApproval }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-5 h-5 text-cyan-400" />
            Bounded Response Briefs
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Grounded disaster briefs synthesized by the 8-State Finite State Machine Agent. High-impact actions require explicit Human Commander sign-off.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {briefs.map(brief => {
          const isPending = brief.approval_status === 'PENDING_HUMAN_APPROVAL';
          const isApproved = brief.approval_status === 'APPROVED';

          return (
            <div key={brief.id} className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-cyan-400">{brief.id}</span>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      isApproved ? 'bg-emerald-950 text-emerald-300 border border-emerald-700' : (isPending ? 'bg-amber-950 text-amber-300 border border-amber-700' : 'bg-rose-950 text-rose-300 border border-rose-700')
                    }`}>
                      {brief.approval_status}
                    </span>
                    <span className="text-xs text-slate-400 font-mono">
                      {new Date(brief.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white mt-1">{brief.target_zone_name}</h3>
                </div>

                <div className="text-right">
                  <div className="text-xs text-slate-400">Risk Severity</div>
                  <div className="text-base font-black text-amber-400">{brief.severity} ({brief.current_risk_score}/100)</div>
                </div>
              </div>

              {/* Evidence Summary */}
              <div>
                <h4 className="text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
                  Evidence Corroboration
                </h4>
                <ul className="space-y-1 text-xs text-slate-300 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  {brief.evidence_summary.map((ev, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-cyan-500 font-bold">•</span>
                      <span>{ev}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Recommended Actions */}
              <div>
                <h4 className="text-xs font-bold text-slate-300 mb-1.5">Proposed Operational Interventions</h4>
                <div className="space-y-1.5">
                  {brief.recommended_actions.map((act, idx) => (
                    <div key={idx} className="text-xs text-slate-200 bg-slate-800/60 px-3 py-2 rounded border border-slate-700/60 flex items-start gap-2">
                      <span className="font-mono text-cyan-400 font-bold">{idx + 1}.</span>
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Verified SOP Citations */}
              {brief.policy_citations && brief.policy_citations.length > 0 && (
                <div>
                  <h4 className="text-xs font-bold text-slate-300 mb-1.5 flex items-center gap-1.5">
                    <BookOpen className="w-3.5 h-3.5 text-purple-400" />
                    Verified Policy Citations
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {brief.policy_citations.map((cit, idx) => (
                      <div key={idx} className="p-2.5 bg-slate-900/80 rounded border border-purple-900/40 text-[11px]">
                        <div className="font-bold text-purple-300">{cit.source_title}</div>
                        <div className="text-slate-400 mt-0.5">{cit.section} (Page {cit.page})</div>
                        <div className="mt-1 font-mono text-[9px] text-slate-500 truncate">SHA256: {cit.content_hash}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Approval status banner or button */}
              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <div className="text-xs text-slate-400 flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-amber-400" />
                  <span>Human-in-the-Loop Gate: <b>Mandatory</b></span>
                </div>

                {isPending ? (
                  <button
                    onClick={() => onOpenApproval(brief)}
                    className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold py-1.5 px-4 rounded-lg shadow-lg hover:shadow-cyan-500/20 transition duration-150 flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    Review & Authorize
                  </button>
                ) : (
                  <div className="text-xs text-emerald-400 font-semibold flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4" />
                    Authorized by {brief.approved_by || 'Commander'}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
