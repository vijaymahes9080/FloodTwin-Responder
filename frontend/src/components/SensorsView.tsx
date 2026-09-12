import React from 'react';
import { SensorReading, RainfallStation } from '../types';
import { Radio, Droplets, Battery, Activity, AlertTriangle, CheckCircle2 } from 'lucide-react';

interface SensorsViewProps {
  sensors: SensorReading[];
  rainfallStations: RainfallStation[];
}

export const SensorsView: React.FC<SensorsViewProps> = ({ sensors, rainfallStations }) => {
  return (
    <div className="space-y-6">
      {/* Stream Gauges Section */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Radio className="w-5 h-5 text-cyan-400" />
          <h2 className="text-lg font-bold text-slate-100">Automated River Stage & Stream Gauges</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {sensors.map(sensor => {
            const isDanger = sensor.water_level_m >= (sensor.danger_threshold_m || 4.0);
            const isWarning = sensor.water_level_m >= (sensor.warning_threshold_m || 3.0);
            const statusColor = isDanger ? 'text-red-400 border-red-800 bg-red-950/30' : (isWarning ? 'text-amber-400 border-amber-800 bg-amber-950/30' : 'text-cyan-400 border-slate-800');

            return (
              <div key={sensor.sensor_id} className={`glass-card rounded-xl p-4 border ${statusColor} flex flex-col justify-between`}>
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-[10px] font-mono text-slate-400 font-bold">{sensor.sensor_id}</span>
                      <h3 className="text-sm font-bold text-white mt-0.5">{sensor.sensor_name || 'River Stage Sensor'}</h3>
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-emerald-400">
                      {sensor.quality_flag}
                    </span>
                  </div>

                  <div className="mt-4 flex items-baseline gap-2">
                    <span className="text-3xl font-black text-white">{sensor.water_level_m}</span>
                    <span className="text-xs text-slate-400 font-semibold">meters stage</span>
                  </div>

                  {/* Visual gauge bar */}
                  <div className="mt-2 w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all ${isDanger ? 'bg-red-500' : (isWarning ? 'bg-amber-500' : 'bg-cyan-400')}`}
                      style={{ width: `${Math.min(100, (sensor.water_level_m / 5.0) * 100)}%` }}
                    />
                  </div>

                  <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                    <span>Base: 1.0m</span>
                    <span>Warn: {sensor.warning_threshold_m || 3.0}m</span>
                    <span>Danger: {sensor.danger_threshold_m || 4.0}m</span>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span className="flex items-center gap-1">
                    <Battery className="w-3.5 h-3.5 text-slate-400" />
                    {sensor.battery_percentage || 100}%
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">
                    {new Date(sensor.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Rainfall Radar / AWS Stations */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Droplets className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-bold text-slate-100">Automated Weather Stations (AWS) Rainfall Telemetry</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {rainfallStations.map(station => (
            <div key={station.station_id} className="glass-card rounded-xl p-4 border border-slate-800">
              <span className="text-[10px] font-mono text-cyan-400 font-bold">{station.station_id}</span>
              <h3 className="text-xs font-bold text-white mt-1 line-clamp-1">{station.station_name}</h3>

              <div className="mt-3 grid grid-cols-3 gap-1 text-center py-2 bg-slate-900/70 rounded-lg">
                <div>
                  <div className="text-base font-black text-blue-400">{station.rain_last_1h_mm}</div>
                  <div className="text-[10px] text-slate-400">1 Hour</div>
                </div>
                <div className="border-x border-slate-800">
                  <div className="text-base font-black text-cyan-400">{station.rain_last_3h_mm}</div>
                  <div className="text-[10px] text-slate-400">3 Hour</div>
                </div>
                <div>
                  <div className="text-base font-black text-indigo-400">{station.rain_last_24h_mm}</div>
                  <div className="text-[10px] text-slate-400">24 Hour</div>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between text-[10px]">
                <span className="text-slate-400 font-semibold">{station.intensity_classification}</span>
                <span className="text-emerald-400 font-mono">ONLINE</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
