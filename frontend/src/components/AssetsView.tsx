import React from 'react';
import { CriticalAsset } from '../types';
import { Building2, HeartPulse, GraduationCap, ShieldAlert, Phone } from 'lucide-react';

interface AssetsViewProps {
  assets: CriticalAsset[];
}

export const AssetsView: React.FC<AssetsViewProps> = ({ assets }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Building2 className="w-5 h-5 text-purple-400" />
            Critical Infrastructure & Healthcare Assets
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Exposure rating evaluated against ground topography elevation and flood protection plinths.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {assets.map(asset => {
          const isHosp = asset.category === 'HOSPITAL';
          const isCriticalExposure = asset.exposure_tier === 'CRITICAL';

          return (
            <div key={asset.id} className="glass-card glass-card-hover rounded-xl p-4 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2">
                    {isHosp ? (
                      <HeartPulse className="w-5 h-5 text-pink-400" />
                    ) : (
                      <GraduationCap className="w-5 h-5 text-purple-400" />
                    )}
                    <span className="text-xs font-bold text-slate-300">{asset.category}</span>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    isCriticalExposure ? 'bg-red-950/80 text-red-300 border border-red-800' : 'bg-purple-950/80 text-purple-300 border border-purple-800'
                  }`}>
                    {asset.exposure_tier} EXPOSURE
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white mt-2">{asset.name}</h3>

                <div className="mt-3 space-y-1 text-xs text-slate-400">
                  <div className="flex justify-between">
                    <span>Ground Elevation:</span>
                    <span className="font-mono text-slate-200">{asset.elevation_m}m MSL</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Distance from Center:</span>
                    <span className="font-mono text-slate-200">{asset.distance_km || 1.8} km</span>
                  </div>
                </div>
              </div>

              {asset.emergency_contact && (
                <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1.5 text-cyan-400">
                    <Phone className="w-3.5 h-3.5" />
                    {asset.emergency_contact}
                  </span>
                  <span className="text-[10px] text-emerald-400 font-semibold">STANDBY READY</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
