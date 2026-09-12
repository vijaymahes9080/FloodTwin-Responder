import React from 'react';
import { RiskTile } from '../types';
import { AlertOctagon, HelpCircle, Activity, ArrowRight, ShieldAlert } from 'lucide-react';

interface RiskTilesViewProps {
  tiles: RiskTile[];
  onDraftBrief: (tileId: string, zoneName: string) => void;
}

export const RiskTilesView: React.FC<RiskTilesViewProps> = ({ tiles, onDraftBrief }) => {
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return 'bg-red-950/80 text-red-300 border-red-700';
      case 'HIGH':
        return 'bg-orange-950/80 text-orange-300 border-orange-700';
      case 'MODERATE':
        return 'bg-amber-950/80 text-amber-300 border-amber-700';
      default:
        return 'bg-blue-950/80 text-blue-300 border-blue-700';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-cyan-400" />
            Explainable Gridded Flood Risk Engine
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Transparent composite scoring. Weights: Rainfall (25%), Sensor Stage (30%), Ground Depth (20%), Elevation (15%), Critical Assets (10%).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tiles.map(tile => (
          <div key={tile.tile_id} className="glass-card glass-card-hover rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
            <div>
              {/* Header */}
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[11px] font-mono text-cyan-400 font-bold tracking-wider">{tile.tile_id}</span>
                  <h3 className="text-lg font-bold text-white mt-0.5">{tile.zone_name}</h3>
                </div>
                <div className="text-right">
                  <div className={`text-xs font-bold px-3 py-1 rounded-full border ${getSeverityBadge(tile.severity)}`}>
                    {tile.severity} SEVERITY
                  </div>
                  <div className="text-2xl font-black text-white mt-1">
                    {tile.risk_score} <span className="text-xs font-normal text-slate-400">/ 100</span>
                  </div>
                </div>
              </div>

              {/* Factor Breakdown Bars */}
              <div className="mt-4 pt-4 border-t border-slate-800 space-y-2.5">
                <div className="text-xs font-bold text-slate-300 flex items-center justify-between">
                  <span>Factor Attribution Breakdown</span>
                  <span className="text-slate-500 text-[10px]">NORMALIZED CONTRIBUTIONS</span>
                </div>

                {/* Rainfall */}
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                    <span>Rainfall Intensity (3h)</span>
                    <span className="text-slate-200">{(tile.factors.rainfall_contribution * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-500 rounded-full" style={{ width: `${tile.factors.rainfall_contribution * 100}%` }} />
                  </div>
                </div>

                {/* Sensor Stage */}
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                    <span>River Stage Telemetry</span>
                    <span className="text-slate-200">{(tile.factors.sensor_water_level_contribution * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-cyan-400 rounded-full" style={{ width: `${tile.factors.sensor_water_level_contribution * 100}%` }} />
                  </div>
                </div>

                {/* Citizen Reports */}
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                    <span>Ground Inundation Reports</span>
                    <span className="text-slate-200">{(tile.factors.citizen_reports_contribution * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-amber-400 rounded-full" style={{ width: `${tile.factors.citizen_reports_contribution * 100}%` }} />
                  </div>
                </div>

                {/* Topography */}
                <div>
                  <div className="flex justify-between text-[11px] text-slate-400 mb-0.5">
                    <span>Low Elevation Vulnerability</span>
                    <span className="text-slate-200">{(tile.factors.elevation_vulnerability_contribution * 100).toFixed(0)}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-orange-400 rounded-full" style={{ width: `${tile.factors.elevation_vulnerability_contribution * 100}%` }} />
                  </div>
                </div>
              </div>

              {/* Uncertainty Metric */}
              <div className="mt-4 p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs">
                <div className="flex items-center justify-between text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <Activity className="w-3.5 h-3.5 text-amber-400" />
                    Data Uncertainty Metric:
                  </span>
                  <span className="font-mono font-bold text-amber-300">{(tile.uncertainty_score * 100).toFixed(0)}%</span>
                </div>
                <div className="mt-1.5 text-[11px] text-slate-400">
                  <b className="text-slate-300">Recommended Next Verification:</b> {tile.recommended_step}
                </div>
              </div>
            </div>

            {/* Action */}
            <button
              onClick={() => onDraftBrief(tile.tile_id, tile.zone_name)}
              className="mt-5 w-full bg-slate-800 hover:bg-cyan-900/40 border border-slate-700 hover:border-cyan-500 text-cyan-300 font-semibold py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition duration-150 text-xs"
            >
              <span>Invoke Bounded Agent: Draft Response Brief</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
