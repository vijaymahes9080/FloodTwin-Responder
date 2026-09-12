import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { FloodReport, SensorReading, CriticalAsset, Shelter, RiskTile } from '../types';
import { Layers, AlertTriangle, ShieldCheck, Eye, Compass } from 'lucide-react';

interface MapViewProps {
  reports: FloodReport[];
  sensors: SensorReading[];
  assets: CriticalAsset[];
  shelters: Shelter[];
  riskTiles: RiskTile[];
  onSelectZone: (zoneId: string, zoneName: string) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  reports,
  sensors,
  assets,
  shelters,
  riskTiles,
  onSelectZone
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  // Layer toggle states
  const [showZones, setShowZones] = useState(true);
  const [showSensors, setShowSensors] = useState(true);
  const [showReports, setShowReports] = useState(true);
  const [showAssets, setShowAssets] = useState(true);
  const [showShelters, setShowShelters] = useState(true);

  const layersRef = useRef<{
    zones: L.LayerGroup;
    sensors: L.LayerGroup;
    reports: L.LayerGroup;
    assets: L.LayerGroup;
    shelters: L.LayerGroup;
  }>({
    zones: L.layerGroup(),
    sensors: L.layerGroup(),
    reports: L.layerGroup(),
    assets: L.layerGroup(),
    shelters: L.layerGroup(),
  });

  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Initialize Leaflet map centered on Chennai Basin
    const map = L.map(mapContainerRef.current, {
      center: [13.045, 80.235],
      zoom: 12,
      zoomControl: true,
      attributionControl: false
    });

    // Dark theme basemap (CartoDB Dark Matter)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd',
    }).addTo(map);

    layersRef.current.zones.addTo(map);
    layersRef.current.sensors.addTo(map);
    layersRef.current.reports.addTo(map);
    layersRef.current.assets.addTo(map);
    layersRef.current.shelters.addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update Layers when data or toggles change
  useEffect(() => {
    const layers = layersRef.current;
    if (!mapInstanceRef.current) return;

    // 1. Risk Zone Polygons
    layers.zones.clearLayers();
    if (showZones) {
      riskTiles.forEach(tile => {
        const [minLon, minLat, maxLon, maxLat] = tile.bbox;
        const color = tile.severity === 'CRITICAL' ? '#ef4444' : (tile.severity === 'HIGH' ? '#f97316' : (tile.severity === 'MODERATE' ? '#eab308' : '#3b82f6'));
        const bounds: L.LatLngBoundsExpression = [[minLat, minLon], [maxLat, maxLon]];
        
        const rect = L.rectangle(bounds, {
          color: color,
          weight: 2,
          fillColor: color,
          fillOpacity: 0.25,
          dashArray: '4, 4'
        });

        rect.bindPopup(`
          <div class="p-2 text-slate-100">
            <div class="font-bold text-sm text-cyan-400">${tile.zone_name}</div>
            <div class="text-xs text-slate-300 mt-1">Severity: <span class="font-semibold text-white">${tile.severity}</span></div>
            <div class="text-xs text-slate-300">Composite Risk Score: <span class="font-bold text-white">${tile.risk_score} / 100</span></div>
            <div class="text-xs text-slate-400 mt-1">Uncertainty: ${(tile.uncertainty_score * 100).toFixed(0)}%</div>
            <button id="btn-${tile.tile_id}" class="mt-2 text-xs bg-cyan-600 hover:bg-cyan-500 text-white px-2 py-1 rounded w-full">Draft Response Brief</button>
          </div>
        `);

        rect.on('popupopen', () => {
          const btn = document.getElementById(`btn-${tile.tile_id}`);
          if (btn) {
            btn.onclick = () => onSelectZone(tile.tile_id, tile.zone_name);
          }
        });

        rect.addTo(layers.zones);
      });
    }

    // 2. Sensors
    layers.sensors.clearLayers();
    if (showSensors) {
      sensors.forEach(s => {
        const lat = s.latitude || 13.04;
        const lon = s.longitude || 80.23;
        const isDanger = s.water_level_m >= (s.danger_threshold_m || 4.0);
        const color = isDanger ? '#ef4444' : '#06b6d4';
        
        const circle = L.circleMarker([lat, lon], {
          radius: 8,
          fillColor: color,
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9
        });

        circle.bindPopup(`
          <div class="p-2 text-slate-100">
            <div class="font-bold text-sm text-cyan-300">${s.sensor_name || s.sensor_id}</div>
            <div class="text-xs text-slate-300 mt-1">Water Stage: <b class="text-white">${s.water_level_m}m</b></div>
            <div class="text-xs text-slate-400">Danger Threshold: ${s.danger_threshold_m || 4.0}m</div>
            <div class="text-xs text-slate-400">Battery: ${s.battery_percentage || 100}%</div>
            <div class="mt-1 text-[10px] bg-slate-800 text-emerald-400 px-1 py-0.5 rounded inline-block font-mono">STATUS: ${s.quality_flag}</div>
          </div>
        `);
        circle.addTo(layers.sensors);
      });
    }

    // 3. Citizen Reports
    layers.reports.clearLayers();
    if (showReports) {
      reports.forEach(r => {
        const lat = r.coordinates.latitude;
        const lon = r.coordinates.longitude;
        const isDuplicate = r.verification_status === 'LIKELY_DUPLICATE';
        
        const marker = L.circleMarker([lat, lon], {
          radius: 6,
          fillColor: isDuplicate ? '#94a3b8' : '#f59e0b',
          color: '#000000',
          weight: 1.5,
          fillOpacity: 0.85
        });

        marker.bindPopup(`
          <div class="p-2 text-slate-100 max-w-xs">
            <div class="font-bold text-xs text-amber-400">${r.verification_status}</div>
            <div class="text-xs text-slate-200 mt-1">${r.description}</div>
            <div class="text-xs text-slate-400 mt-1">Depth: ${r.reported_depth_cm ? r.reported_depth_cm + 'cm' : 'Not specified'}</div>
            <div class="text-[10px] text-cyan-400 mt-1 font-mono">Credibility Confidence: ${(r.confidence * 100).toFixed(0)}%</div>
          </div>
        `);
        marker.addTo(layers.reports);
      });
    }

    // 4. Critical Assets (Hospitals / Schools)
    layers.assets.clearLayers();
    if (showAssets) {
      assets.forEach(a => {
        const lat = a.latitude;
        const lon = a.longitude;
        const isHosp = a.category === 'HOSPITAL';
        const marker = L.circleMarker([lat, lon], {
          radius: 7,
          fillColor: isHosp ? '#ec4899' : '#8b5cf6',
          color: '#ffffff',
          weight: 1.5,
          fillOpacity: 0.9
        });

        marker.bindPopup(`
          <div class="p-2 text-slate-100">
            <div class="font-bold text-xs text-purple-300">${a.name}</div>
            <div class="text-xs text-slate-400">Category: ${a.category}</div>
            <div class="text-xs text-slate-400">Elevation: ${a.elevation_m}m MSL</div>
            <div class="text-xs text-red-400 font-semibold mt-1">Exposure: ${a.exposure_tier}</div>
          </div>
        `);
        marker.addTo(layers.assets);
      });
    }

    // 5. Shelters
    layers.shelters.clearLayers();
    if (showShelters) {
      shelters.forEach(sh => {
        const lat = sh.latitude;
        const lon = sh.longitude;
        const marker = L.circleMarker([lat, lon], {
          radius: 7,
          fillColor: '#10b981',
          color: '#ffffff',
          weight: 1.5,
          fillOpacity: 0.9
        });

        marker.bindPopup(`
          <div class="p-2 text-slate-100">
            <div class="font-bold text-xs text-emerald-400">${sh.name}</div>
            <div class="text-xs text-slate-300 mt-1">Capacity: ${sh.available_capacity || (sh.total_capacity - sh.current_occupancy)} / ${sh.total_capacity} beds</div>
            <div class="text-xs text-slate-400">Status: <span class="text-emerald-300 font-semibold">${sh.operational_status}</span></div>
            <div class="text-xs text-slate-400 mt-1">Helpline: ${sh.emergency_contact}</div>
          </div>
        `);
        marker.addTo(layers.shelters);
      });
    }

  }, [reports, sensors, assets, shelters, riskTiles, showZones, showSensors, showReports, showAssets, showShelters, onSelectZone]);

  return (
    <div className="relative w-full h-[640px] rounded-xl overflow-hidden glass-card shadow-2xl">
      {/* Leaflet container */}
      <div ref={mapContainerRef} className="w-full h-full z-0" />

      {/* Floating Layer Controls */}
      <div className="absolute top-4 right-4 z-[1000] bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-lg p-3 shadow-xl text-xs space-y-2">
        <div className="flex items-center gap-1.5 font-bold text-cyan-400 pb-1 border-b border-slate-700">
          <Layers className="w-3.5 h-3.5" />
          <span>GEOSPATIAL LAYERS</span>
        </div>
        <label className="flex items-center gap-2 cursor-pointer text-slate-200 hover:text-white">
          <input type="checkbox" checked={showZones} onChange={e => setShowZones(e.target.checked)} className="rounded bg-slate-800 border-slate-600 text-cyan-500 focus:ring-0" />
          <span className="w-2.5 h-2.5 rounded-full bg-orange-500 inline-block"></span>
          Risk Tiles ({riskTiles.length})
        </label>
        <label className="flex items-center gap-2 cursor-pointer text-slate-200 hover:text-white">
          <input type="checkbox" checked={showSensors} onChange={e => setShowSensors(e.target.checked)} className="rounded bg-slate-800 border-slate-600 text-cyan-500 focus:ring-0" />
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 inline-block"></span>
          Water Stage Sensors ({sensors.length})
        </label>
        <label className="flex items-center gap-2 cursor-pointer text-slate-200 hover:text-white">
          <input type="checkbox" checked={showReports} onChange={e => setShowReports(e.target.checked)} className="rounded bg-slate-800 border-slate-600 text-cyan-500 focus:ring-0" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block"></span>
          Citizen Reports ({reports.length})
        </label>
        <label className="flex items-center gap-2 cursor-pointer text-slate-200 hover:text-white">
          <input type="checkbox" checked={showAssets} onChange={e => setShowAssets(e.target.checked)} className="rounded bg-slate-800 border-slate-600 text-cyan-500 focus:ring-0" />
          <span className="w-2.5 h-2.5 rounded-full bg-purple-400 inline-block"></span>
          Critical Assets ({assets.length})
        </label>
        <label className="flex items-center gap-2 cursor-pointer text-slate-200 hover:text-white">
          <input type="checkbox" checked={showShelters} onChange={e => setShowShelters(e.target.checked)} className="rounded bg-slate-800 border-slate-600 text-cyan-500 focus:ring-0" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block"></span>
          Relief Shelters ({shelters.length})
        </label>
      </div>

      {/* CRS Badge */}
      <div className="absolute bottom-3 left-4 z-[1000] bg-slate-900/85 backdrop-blur-md border border-slate-700/80 px-2.5 py-1 rounded text-[11px] font-mono text-slate-300 flex items-center gap-1.5">
        <Compass className="w-3.5 h-3.5 text-cyan-400 animate-spin" style={{ animationDuration: '12s' }} />
        <span>CRS: EPSG:4326 (WGS 84) | CHENNAI BASIN</span>
      </div>
    </div>
  );
};
