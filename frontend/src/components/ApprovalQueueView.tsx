import React, { useState } from 'react';
import { ResponseBrief } from '../types';
import { ShieldCheck, XCircle, CheckCircle2, AlertTriangle, Send, UserCheck } from 'lucide-react';

interface ApprovalQueueViewProps {
  briefs: ResponseBrief[];
  onApprove: (briefId: string, comments: string) => Promise<void>;
  onReject: (briefId: string, comments: string) => Promise<void>;
}

export const ApprovalQueueView: React.FC<ApprovalQueueViewProps> = ({
  briefs,
  onApprove,
  onReject
}) => {
  const [selectedBrief, setSelectedBrief] = useState<ResponseBrief | null>(null);
  const [comments, setComments] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  const pendingBriefs = briefs.filter(b => b.approval_status === 'PENDING_HUMAN_APPROVAL');

  const handleAction = async (decision: 'APPROVE' | 'REJECT') => {
    if (!selectedBrief) return;
    setIsProcessing(true);
    try {
      if (decision === 'APPROVE') {
        await onApprove(selectedBrief.id, comments || 'Approved by Incident Commander under standard operating guidelines.');
        setActionSuccess(`Brief ${selectedBrief.id} APPROVED! Mock simulation alert payload dispatched.`);
      } else {
        await onReject(selectedBrief.id, comments || 'Rejected by Incident Commander. Further field inspection required.');
        setActionSuccess(`Brief ${selectedBrief.id} REJECTED.`);
      }
      setSelectedBrief(null);
      setComments('');
    } catch (err: any) {
      alert(err.message || 'Action failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-amber-400" />
            Human Commander Approval Queue
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Mandatory human authorization checkpoint. System invariants unconditionally bar autonomous response dispatch.
          </p>
        </div>
      </div>

      {actionSuccess && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-700 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {pendingBriefs.length === 0 ? (
        <div className="glass-card rounded-xl p-12 text-center border border-slate-800">
          <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3 opacity-80" />
          <h3 className="text-lg font-bold text-white">Approval Queue Clear</h3>
          <p className="text-xs text-slate-400 mt-1">No response briefs are currently awaiting human authorization.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pendingBriefs.map(brief => (
            <div key={brief.id} className="glass-card rounded-xl p-5 border border-amber-900/40 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-mono font-bold text-amber-400">{brief.id}</span>
                  <h3 className="text-base font-bold text-white mt-1">{brief.target_zone_name}</h3>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700">
                    AWAITING COMMANDER
                  </span>
                  <div className="text-xs font-bold text-white mt-1">Risk: {brief.current_risk_score}/100</div>
                </div>
              </div>

              <div className="text-xs text-slate-300 space-y-1">
                <div className="font-semibold text-slate-200">Summary Evidence:</div>
                <ul className="list-disc list-inside text-slate-400 text-[11px] space-y-0.5">
                  {brief.evidence_summary.slice(0, 2).map((e, idx) => (
                    <li key={idx} className="truncate">{e}</li>
                  ))}
                </ul>
              </div>

              <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-2">
                <button
                  onClick={() => setSelectedBrief(brief)}
                  className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold py-1.5 px-4 rounded-lg shadow transition"
                >
                  Review Decision
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Review Modal */}
      {selectedBrief && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-card bg-slate-900 border border-slate-700 max-w-xl w-full rounded-2xl p-6 space-y-4 shadow-2xl">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-mono text-cyan-400 font-bold">{selectedBrief.id}</span>
                <h3 className="text-lg font-bold text-white">{selectedBrief.target_zone_name}</h3>
              </div>
              <button
                onClick={() => setSelectedBrief(null)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* Simulation Warning Banner */}
            <div className="p-3 bg-amber-950/60 border border-amber-800 rounded-lg text-xs text-amber-300 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
              <span>
                <b>Safety Notice:</b> Approving this brief emits a simulated mock dispatch payload only. Zero live siren or cellular emergency broadcasts will be initiated.
              </span>
            </div>

            {/* Recommended actions */}
            <div className="space-y-1 text-xs">
              <div className="font-bold text-slate-300">Actions Staged for Authorization:</div>
              {selectedBrief.recommended_actions.map((act, i) => (
                <div key={i} className="p-2 bg-slate-800/80 rounded border border-slate-700/60 text-slate-200">
                  {i + 1}. {act}
                </div>
              ))}
            </div>

            {/* Commander comments input */}
            <div>
              <label className="block text-xs font-bold text-slate-300 mb-1">
                Commander Authorization Rationale (Recorded in Merkle Audit Chain):
              </label>
              <textarea
                rows={2}
                value={comments}
                onChange={e => setComments(e.target.value)}
                placeholder="e.g. Authorized mobilization of SDRF rescue boats and dewatering suction units..."
                className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
              />
            </div>

            {/* Actions */}
            <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
              <button
                type="button"
                disabled={isProcessing}
                onClick={() => handleAction('REJECT')}
                className="px-4 py-2 bg-rose-950/80 hover:bg-rose-900 border border-rose-800 text-rose-300 text-xs font-bold rounded-lg transition"
              >
                Reject Brief
              </button>
              <button
                type="button"
                disabled={isProcessing}
                onClick={() => handleAction('APPROVE')}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow-lg hover:shadow-emerald-500/20 transition flex items-center gap-2"
              >
                <CheckCircle2 className="w-4 h-4" />
                Authorize & Trigger Mock Dispatch
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
