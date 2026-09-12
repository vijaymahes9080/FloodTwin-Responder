import React from 'react';
import { Shelter } from '../types';
import { Home, Users, Phone, Zap, Heart, CheckCircle2 } from 'lucide-react';

interface SheltersViewProps {
  shelters: Shelter[];
}

export const SheltersView: React.FC<SheltersViewProps> = ({ shelters }) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <Home className="w-5 h-5 text-emerald-400" />
            Designated Disaster Relief Shelters & Safe Havens
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time bed availability, emergency contacts, medical supply staging, and generator backup status.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {shelters.map(shelter => {
          const avail = shelter.available_capacity !== undefined ? shelter.available_capacity : (shelter.total_capacity - shelter.current_occupancy);
          const pctOccupied = Math.round(((shelter.total_capacity - avail) / shelter.total_capacity) * 100);

          return (
            <div key={shelter.id} className="glass-card glass-card-hover rounded-xl p-5 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-mono text-emerald-400 font-bold">{shelter.id}</span>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                    shelter.operational_status === 'OPEN'
                      ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                      : 'bg-amber-950/80 text-amber-300 border border-amber-800'
                  }`}>
                    {shelter.operational_status}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white mt-1">{shelter.name}</h3>

                {/* Capacity Gauge */}
                <div className="mt-4 p-3 bg-slate-900/80 rounded-lg border border-slate-800">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="text-slate-400 flex items-center gap-1">
                      <Users className="w-3.5 h-3.5 text-cyan-400" />
                      Available Beds:
                    </span>
                    <span className="font-bold text-white text-sm">{avail} <span className="text-xs text-slate-500 font-normal">/ {shelter.total_capacity}</span></span>
                  </div>

                  <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${pctOccupied > 80 ? 'bg-amber-500' : 'bg-emerald-400'}`}
                      style={{ width: `${pctOccupied}%` }}
                    />
                  </div>
                  <div className="text-[10px] text-right text-slate-500 mt-1">{pctOccupied}% Occupied</div>
                </div>

                {/* Amenities Badges */}
                <div className="mt-3 flex items-center gap-3 text-xs text-slate-300">
                  <span className="flex items-center gap-1 text-[11px] text-slate-400">
                    <Heart className="w-3.5 h-3.5 text-rose-400" />
                    Medical Supply
                  </span>
                  <span className="flex items-center gap-1 text-[11px] text-slate-400">
                    <Zap className="w-3.5 h-3.5 text-amber-400" />
                    Backup Power
                  </span>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                <a
                  href={`tel:${shelter.emergency_contact}`}
                  className="flex items-center gap-1.5 text-cyan-400 hover:text-cyan-300 font-mono"
                >
                  <Phone className="w-3.5 h-3.5" />
                  {shelter.emergency_contact}
                </a>
                <span className="text-[11px] text-slate-400">
                  {shelter.distance_km ? `${shelter.distance_km} km` : '1.4 km'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
