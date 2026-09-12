import React, { useState, useEffect } from 'react';
import { translations, Language } from './i18n';
import {
  FloodReport,
  SensorReading,
  RainfallStation,
  RiskTile,
  CriticalAsset,
  Shelter,
  ResponseBrief,
  AuditEvent
} from './types';

// Views
import { MapView } from './components/MapView';
import { ReportsView } from './components/ReportsView';
import { RiskTilesView } from './components/RiskTilesView';
import { SensorsView } from './components/SensorsView';
import { AssetsView } from './components/AssetsView';
import { SheltersView } from './components/SheltersView';
import { BriefsView } from './components/BriefsView';
import { ApprovalQueueView } from './components/ApprovalQueueView';
import { EvidenceView } from './components/EvidenceView';
import { AuditView } from './components/AuditView';
import { BenchmarkView } from './components/BenchmarkView';

// Icons
import {
  Map,
  Inbox,
  ShieldAlert,
  Radio,
  Building2,
  Home,
  FileText,
  UserCheck,
  BookOpen,
  Link2,
  Award,
  RefreshCw,
  AlertTriangle,
  Globe,
  User
} from 'lucide-react';

export const App: React.FC = () => {
  const [lang, setLang] = useState<Language>('en');
  const t = translations[lang];

  const [activeTab, setActiveTab] = useState<string>('map');
  const [isLoading, setIsLoading] = useState(false);

  // Core Data State
  const [reports, setReports] = useState<FloodReport[]>([]);
  const [sensors, setSensors] = useState<SensorReading[]>([]);
  const [rainfallStations, setRainfallStations] = useState<RainfallStation[]>([]);
  const [riskTiles, setRiskTiles] = useState<RiskTile[]>([]);
  const [criticalAssets, setCriticalAssets] = useState<CriticalAsset[]>([]);
  const [shelters, setShelters] = useState<Shelter[]>([]);
  const [responseBriefs, setResponseBriefs] = useState<ResponseBrief[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);

  // Active brief for review modal
  const [reviewBrief, setReviewBrief] = useState<ResponseBrief | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      // 1. Reports
      const repRes = await fetch('/api/v1/reports');
      if (repRes.ok) {
        const d = await repRes.json();
        setReports(d.reports || []);
      }

      // 2. Sensors
      const sensRes = await fetch('/api/v1/sensors/status');
      if (sensRes.ok) {
        const d = await sensRes.json();
        setSensors(d.water_level_sensors || []);
        setRainfallStations(d.rainfall_stations || []);
      }

      // 3. Risk Tiles
      const riskRes = await fetch('/api/v1/risk/tiles');
      if (riskRes.ok) {
        const d = await riskRes.json();
        setRiskTiles(d.tiles || []);
      }

      // 4. Assets & Shelters
      const assetRes = await fetch('/api/v1/assets/nearby?latitude=13.04&longitude=80.23&radius_km=15.0');
      if (assetRes.ok) {
        const d = await assetRes.json();
        setCriticalAssets(d.assets || []);
      }

      const shelterRes = await fetch('/api/v1/shelters/nearby?latitude=13.04&longitude=80.23&max_distance_km=20.0');
      if (shelterRes.ok) {
        const d = await shelterRes.json();
        setShelters(d.shelters || []);
      }

      // 5. Briefs
      const briefRes = await fetch('/api/v1/response-briefs');
      if (briefRes.ok) {
        const d = await briefRes.json();
        setResponseBriefs(d.response_briefs || []);
      }

      // 6. Audit
      const auditRes = await fetch('/api/v1/audit?limit=30');
      if (auditRes.ok) {
        const d = await auditRes.json();
        setAuditEvents(d.events || []);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateReport = async (reportData: any) => {
    const res = await fetch('/api/v1/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reportData)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail?.reason || 'Failed to submit report');
    }
    await fetchData();
  };

  const handleDraftBrief = async (zoneId: string, zoneName: string) => {
    const res = await fetch('/api/v1/response-briefs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        zone_id: zoneId,
        zone_name: zoneName,
        latitude: 13.018,
        longitude: 80.222
      })
    });
    if (res.ok) {
      await fetchData();
      setActiveTab('briefs');
    }
  };

  const handleApproveBrief = async (briefId: string, comments: string) => {
    const res = await fetch(`/api/v1/response-briefs/${briefId}/approve`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-operator-key': 'cmd_kumar'
      },
      body: JSON.stringify({ operator_comments: comments })
    });
    if (!res.ok) throw new Error('Approval failed');
    await fetchData();
  };

  const handleRejectBrief = async (briefId: string, comments: string) => {
    const res = await fetch(`/api/v1/response-briefs/${briefId}/reject`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-operator-key': 'cmd_kumar'
      },
      body: JSON.stringify({ operator_comments: comments })
    });
    if (!res.ok) throw new Error('Rejection failed');
    await fetchData();
  };

  const navItems = [
    { id: 'map', label: t.nav.map, icon: Map, count: null },
    { id: 'reports', label: t.nav.reports, icon: Inbox, count: reports.length },
    { id: 'riskTiles', label: t.nav.riskTiles, icon: ShieldAlert, count: riskTiles.length },
    { id: 'sensors', label: t.nav.sensors, icon: Radio, count: sensors.length },
    { id: 'assets', label: t.nav.assets, icon: Building2, count: criticalAssets.length },
    { id: 'shelters', label: t.nav.shelters, icon: Home, count: shelters.length },
    { id: 'briefs', label: t.nav.briefs, icon: FileText, count: responseBriefs.length },
    { id: 'approvals', label: t.nav.approvals, icon: UserCheck, count: responseBriefs.filter(b => b.approval_status === 'PENDING_HUMAN_APPROVAL').length },
    { id: 'evidence', label: t.nav.evidence, icon: BookOpen, count: null },
    { id: 'audit', label: t.nav.audit, icon: Link2, count: auditEvents.length },
    { id: 'benchmarks', label: t.nav.benchmarks, icon: Award, count: null }
  ];

  return (
    <div className="min-h-screen bg-[#0a0f1d] text-slate-100 flex flex-col font-sans">
      {/* 1. Universal Top Warning Banner */}
      <div className="bg-amber-950/90 border-b border-amber-800/80 px-4 py-1.5 text-center text-xs font-bold text-amber-300 flex items-center justify-center gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        <span>{t.sandboxBanner}</span>
      </div>

      {/* 2. Top Header Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tight text-white flex items-center gap-2">
              {t.appTitle}
              <span className="text-[10px] font-mono font-bold bg-cyan-950 text-cyan-400 border border-cyan-800 px-2 py-0.5 rounded">
                v1.0-PROD
              </span>
            </h1>
            <p className="text-[11px] text-slate-400">{t.appSubtitle}</p>
          </div>
        </div>

        {/* Right Header Controls */}
        <div className="flex items-center gap-4 text-xs">
          {/* District Tag */}
          <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>{t.operationalDistrict}</span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>{t.common.refresh}</span>
          </button>

          {/* Bilingual Toggle */}
          <button
            onClick={() => setLang(lang === 'en' ? 'ta' : 'en')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 border border-slate-700 font-bold transition"
          >
            <Globe className="w-3.5 h-3.5" />
            <span>{lang === 'en' ? 'தமிழ் (TA)' : 'English (EN)'}</span>
          </button>

          {/* Operator Profile */}
          <div className="flex items-center gap-2 pl-3 border-l border-slate-800">
            <div className="w-7 h-7 rounded-full bg-cyan-950 border border-cyan-800 flex items-center justify-center text-cyan-300">
              <User className="w-4 h-4" />
            </div>
            <div className="hidden lg:block text-left">
              <div className="font-bold text-white leading-tight">Dr. Senthil Kumar</div>
              <div className="text-[10px] text-amber-400 font-mono">DISASTER COMMANDER</div>
            </div>
          </div>
        </div>
      </header>

      {/* 3. Main Workspace with Sidebar */}
      <div className="flex-1 flex overflow-hidden">
        {/* Navigation Sidebar */}
        <aside className="w-64 border-r border-slate-800/80 bg-slate-900/40 p-3 space-y-1 overflow-y-auto shrink-0">
          <div className="text-[10px] font-mono font-bold text-slate-500 uppercase px-3 py-2 tracking-wider">
            Operational Views (11)
          </div>

          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold transition ${
                  isActive
                    ? 'bg-cyan-600/20 text-cyan-300 border border-cyan-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </div>
                {item.count !== null && (
                  <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full ${
                    isActive ? 'bg-cyan-500/30 text-cyan-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {item.count}
                  </span>
                )}
              </button>
            );
          })}
        </aside>

        {/* Dynamic View Canvas */}
        <main className="flex-1 p-6 overflow-y-auto bg-[#0a0f1d]">
          {activeTab === 'map' && (
            <MapView
              reports={reports}
              sensors={sensors}
              assets={criticalAssets}
              shelters={shelters}
              riskTiles={riskTiles}
              onSelectZone={(zid, zname) => handleDraftBrief(zid, zname)}
            />
          )}

          {activeTab === 'reports' && (
            <ReportsView
              reports={reports}
              onSubmitReport={handleCreateReport}
            />
          )}

          {activeTab === 'riskTiles' && (
            <RiskTilesView
              tiles={riskTiles}
              onDraftBrief={(zid, zname) => handleDraftBrief(zid, zname)}
            />
          )}

          {activeTab === 'sensors' && (
            <SensorsView
              sensors={sensors}
              rainfallStations={rainfallStations}
            />
          )}

          {activeTab === 'assets' && (
            <AssetsView assets={criticalAssets} />
          )}

          {activeTab === 'shelters' && (
            <SheltersView shelters={shelters} />
          )}

          {activeTab === 'briefs' && (
            <BriefsView
              briefs={responseBriefs}
              onOpenApproval={b => {
                setActiveTab('approvals');
              }}
            />
          )}

          {activeTab === 'approvals' && (
            <ApprovalQueueView
              briefs={responseBriefs}
              onApprove={handleApproveBrief}
              onReject={handleRejectBrief}
            />
          )}

          {activeTab === 'evidence' && (
            <EvidenceView />
          )}

          {activeTab === 'audit' && (
            <AuditView auditEvents={auditEvents} />
          )}

          {activeTab === 'benchmarks' && (
            <BenchmarkView />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
