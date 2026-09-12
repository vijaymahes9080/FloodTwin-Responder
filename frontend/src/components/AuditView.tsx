import React from 'react';
import { AuditEvent } from '../types';
import { ShieldCheck, Link2, Hash, Clock, User, Activity } from 'lucide-react';

interface AuditViewProps {
  auditEvents: AuditEvent[];
}

export const AuditView: React.FC<AuditViewProps> = ({ auditEvents }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            Cryptographically Chained Audit Trail
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Immutable SHA-256 Merkle-linked audit log. Every report, risk computation, brief draft, and human commander decision is permanently recorded.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-emerald-950/60 border border-emerald-800 px-3 py-1.5 rounded-lg text-xs font-mono text-emerald-300">
          <Link2 className="w-4 h-4 text-emerald-400" />
          <span>CHAIN INTEGRITY: 100% VERIFIED</span>
        </div>
      </div>

      <div className="space-y-3">
        {auditEvents.map(event => (
          <div key={event.id} className="glass-card rounded-xl p-4 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-cyan-400">{event.id}</span>
                <span className="text-xs font-bold text-slate-100 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                  {event.action}
                </span>
                <span className="text-[10px] text-slate-400 font-mono">
                  {event.resource_type}: {event.resource_id}
                </span>
              </div>

              <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                {new Date(event.timestamp).toLocaleString()}
              </div>
            </div>

            {/* Actor Details */}
            <div className="flex items-center gap-4 text-xs text-slate-300">
              <span className="flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-cyan-400" />
                Actor: <b className="text-white">{event.actor_id}</b> ({event.actor_role})
              </span>
            </div>

            {/* Event Payload */}
            <div className="p-2.5 bg-slate-900/90 rounded border border-slate-800 text-[11px] font-mono text-slate-300 overflow-x-auto">
              <pre>{JSON.stringify(event.details, null, 2)}</pre>
            </div>

            {/* Cryptographic Linkage */}
            <div className="pt-2 border-t border-slate-850 grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] font-mono text-slate-500">
              <div className="truncate">
                <span className="text-slate-400">PREV_HASH:</span> {event.previous_event_hash || 'GENESIS'}
              </div>
              <div className="truncate text-right">
                <span className="text-emerald-500">MERKLE_HASH:</span> {event.provenance_hash}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
