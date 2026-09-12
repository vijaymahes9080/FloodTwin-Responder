import React, { useState, useEffect } from 'react';
import { PolicyCitation } from '../types';
import { BookOpen, Search, ShieldCheck, Hash, FileText } from 'lucide-react';

export const EvidenceView: React.FC = () => {
  const [query, setQuery] = useState('hospital emergency generator elevation rooftop flood SOP');
  const [citations, setCitations] = useState<PolicyCitation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [allSOPs, setAllSOPs] = useState<any[]>([]);

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setIsLoading(true);
    try {
      const res = await fetch(`/api/v1/policy/search?query=${encodeURIComponent(searchQuery)}&top_k=3`);
      if (res.ok) {
        const data = await res.json();
        setCitations(data.citations || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleSearch(query);
    // Fetch all indexed SOPs
    fetch('/api/v1/policy/all')
      .then(res => res.json())
      .then(data => setAllSOPs(data.documents || []))
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-400" />
            Verified Policy & SOP Knowledge Base (RAG)
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Grounded disaster management guidelines. Every brief recommendation is backed by a verified document, section, page, and SHA-256 hash.
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="glass-card rounded-xl p-4 border border-slate-800">
        <form
          onSubmit={e => {
            e.preventDefault();
            handleSearch(query);
          }}
          className="flex gap-3"
        >
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search emergency SOPs e.g. transformer substation shutdown, livestock mound..."
              className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-purple-500"
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs px-5 py-2 rounded-lg transition"
          >
            {isLoading ? 'Querying...' : 'Search SOPs'}
          </button>
        </form>
      </div>

      {/* Citations Results */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          Semantic Top-K Retrieved SOP Citations ({citations.length})
        </h3>

        <div className="space-y-3">
          {citations.map((cit, idx) => (
            <div key={idx} className="glass-card rounded-xl p-5 border border-purple-900/40 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="text-sm font-bold text-purple-300">{cit.source_title}</h4>
                  <div className="text-xs text-slate-400 mt-0.5">
                    <b>{cit.section}</b> • Page <span className="font-mono text-cyan-400 font-bold">{cit.page}</span>
                  </div>
                  <div className="text-[11px] text-slate-500 mt-0.5">{cit.jurisdiction} • Published {cit.publication_date}</div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] font-mono bg-purple-950/80 border border-purple-800 text-purple-300 px-2 py-0.5 rounded-full font-bold">
                    RELEVANCE: {(cit.relevance_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="p-3 bg-slate-900/80 rounded-lg border border-slate-800 text-xs text-slate-200 leading-relaxed font-sans">
                "{cit.full_content}"
              </div>

              <div className="flex items-center gap-1.5 font-mono text-[10px] text-slate-500 truncate">
                <Hash className="w-3 h-3 text-cyan-400 shrink-0" />
                <span>SHA-256 INTEGRITY: {cit.content_hash}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Indexed Library Explorer */}
      <div>
        <h3 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-1.5">
          <FileText className="w-4 h-4 text-slate-400" />
          Official Disaster SOP Repository Master Index ({allSOPs.length})
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {allSOPs.map(sop => (
            <div key={sop.id} className="p-3 glass-card rounded-lg border border-slate-800 text-xs space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] text-cyan-400 font-bold">{sop.id}</span>
                <span className="text-[10px] text-slate-400 font-mono">Page {sop.page_number}</span>
              </div>
              <div className="font-bold text-slate-200 line-clamp-1">{sop.title}</div>
              <div className="text-[11px] text-slate-400 line-clamp-1">{sop.section}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
