import React, { useState } from 'react';
import { FloodReport } from '../types';
import { ShieldCheck, AlertCircle, Copy, Send, Filter, CheckCircle2, MapPin } from 'lucide-react';

interface ReportsViewProps {
  reports: FloodReport[];
  onSubmitReport: (report: any) => Promise<void>;
}

export const ReportsView: React.FC<ReportsViewProps> = ({ reports, onSubmitReport }) => {
  const [filter, setFilter] = useState<string>('ALL');
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState(13.018);
  const [longitude, setLongitude] = useState(80.222);
  const [depthCm, setDepthCm] = useState(45);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMsg, setSubmitMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const filtered = reports.filter(r => {
    if (filter === 'ALL') return true;
    if (filter === 'DUPLICATES') return r.verification_status === 'LIKELY_DUPLICATE';
    if (filter === 'UNVERIFIED') return r.verification_status === 'POSSIBLE_WATERLOGGING';
    return true;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMsg(null);
    try {
      await onSubmitReport({
        description,
        latitude: parseFloat(latitude.toString()),
        longitude: parseFloat(longitude.toString()),
        reported_depth_cm: parseFloat(depthCm.toString()),
        source: 'CITIZEN_APP'
      });
      setSubmitMsg({ type: 'success', text: 'Report ingested! Coordinate verified & PII redacted.' });
      setDescription('');
    } catch (err: any) {
      setSubmitMsg({ type: 'error', text: err.message || 'Failed to ingest report.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Submit Report Form */}
      <div className="glass-card rounded-xl p-5 border border-slate-800 shadow-xl h-fit">
        <div className="flex items-center gap-2 mb-4 text-cyan-400">
          <Send className="w-5 h-5" />
          <h2 className="text-lg font-bold">Ingest Ground Report</h2>
        </div>
        <p className="text-xs text-slate-400 mb-4">
          All inputs treated as untrusted. Automatic coordinate bounding and PII scrubbing will be applied before storage.
        </p>

        {submitMsg && (
          <div className={`p-3 rounded-lg text-xs mb-4 ${submitMsg.type === 'success' ? 'bg-emerald-950/60 border border-emerald-700 text-emerald-300' : 'bg-rose-950/60 border border-rose-700 text-rose-300'}`}>
            {submitMsg.text}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block text-slate-300 font-semibold mb-1">Observation Description</label>
            <textarea
              required
              rows={3}
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="e.g. Heavy waterlogging near Saidapet bazaar, phone 9840112233..."
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Latitude (12.8 - 13.3)</label>
              <input
                type="number"
                step="0.001"
                required
                value={latitude}
                onChange={e => setLatitude(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-100 focus:border-cyan-500"
              />
            </div>
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Longitude (79.9 - 80.4)</label>
              <input
                type="number"
                step="0.001"
                required
                value={longitude}
                onChange={e => setLongitude(parseFloat(e.target.value))}
                className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-100 focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-slate-300 font-semibold mb-1">Reported Depth (cm)</label>
            <input
              type="number"
              min="0"
              max="300"
              value={depthCm}
              onChange={e => setDepthCm(parseFloat(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-slate-100 focus:border-cyan-500"
            />
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-semibold py-2 px-4 rounded transition duration-200 disabled:opacity-50"
          >
            {isSubmitting ? 'Evaluating QC Rules...' : 'Submit to Disaster QC Engine'}
          </button>
        </form>
      </div>

      {/* Reports Feed */}
      <div className="lg:col-span-2 space-y-4">
        {/* Controls */}
        <div className="flex items-center justify-between glass-card p-3 rounded-lg text-xs">
          <div className="flex items-center gap-2 text-slate-300">
            <Filter className="w-4 h-4 text-cyan-400" />
            <span className="font-semibold">Filter Feed:</span>
            <button
              onClick={() => setFilter('ALL')}
              className={`px-2.5 py-1 rounded ${filter === 'ALL' ? 'bg-cyan-600 text-white' : 'bg-slate-800 text-slate-300'}`}
            >
              All ({reports.length})
            </button>
            <button
              onClick={() => setFilter('DUPLICATES')}
              className={`px-2.5 py-1 rounded ${filter === 'DUPLICATES' ? 'bg-cyan-600 text-white' : 'bg-slate-800 text-slate-300'}`}
            >
              Duplicates
            </button>
          </div>
          <span className="text-slate-400 font-mono">ENVELOPE: CHENNAI_DISTRICT</span>
        </div>

        {/* List */}
        <div className="space-y-3">
          {filtered.map(report => (
            <div key={report.id} className="glass-card glass-card-hover rounded-xl p-4 border border-slate-800">
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-cyan-400 font-bold">{report.id}</span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                      report.verification_status === 'LIKELY_DUPLICATE'
                        ? 'bg-slate-800 text-slate-400 border border-slate-700'
                        : 'bg-amber-950/70 text-amber-300 border border-amber-800'
                    }`}>
                      {report.verification_status}
                    </span>
                    {report.duplicate_of && (
                      <span className="text-[10px] text-slate-400 font-mono">
                        Dup of: <span className="text-cyan-400">{report.duplicate_of}</span>
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-200 mt-2">{report.description}</p>
                </div>

                <div className="text-right text-xs">
                  <div className="text-slate-400">Credibility</div>
                  <div className="font-bold text-emerald-400">{(report.confidence * 100).toFixed(0)}%</div>
                </div>
              </div>

              {/* Footer Meta */}
              <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                <div className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3 h-3 text-cyan-500" />
                    {report.coordinates.latitude.toFixed(4)}, {report.coordinates.longitude.toFixed(4)}
                  </span>
                  <span>Depth: <b className="text-slate-200">{report.reported_depth_cm ? `${report.reported_depth_cm} cm` : 'N/A'}</b></span>
                </div>
                <div className="text-slate-500 font-mono">
                  {new Date(report.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
