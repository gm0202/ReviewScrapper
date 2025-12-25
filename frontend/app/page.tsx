"use client"

import { useState } from 'react';
import axios from 'axios';
import { Search, Loader2, Zap, Flame, Download } from 'lucide-react';
import TrendChart from '@/components/TrendChart';
import InsightPanel from '@/components/InsightPanel';

// Types
interface AnalysisResult {
  topics: string[];
  trend: Record<string, number[]>;
  dates: string[];
  newTopics: string[];
  spikes: string[];
  insights: string;
}

export default function Home() {
  const [appName, setAppName] = useState('Instagram');
  const [dates, setDates] = useState(() => {
    const today = new Date().toISOString().split('T')[0];
    return [today, today];
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Robust URL handling
      let apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
      // Remove trailing slash to prevent double slash (//) errors
      apiUrl = apiUrl.replace(/\/$/, "");

      if (!apiUrl.startsWith('http')) {
        apiUrl = `https://${apiUrl}`;
      }

      const resp = await axios.post(`${apiUrl}/analyze`, {
        app_name: appName,
        dates: dates
      });
      setResult(resp.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Analysis failed. Make sure Backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCSV = () => {
    if (!result) return;

    // Header
    const headers = ['Topic', ...result.dates];
    const rows = result.topics.map(topic => {
      const rowData = result.trend[topic].map(val => val || 0);
      return [topic, ...rowData].join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${appName}_trend_report.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Helper to format data for Recharts
  const chartData = result?.dates.map((date, idx) => {
    const obj: any = { date };
    result.topics.forEach(t => {
      obj[t] = result.trend[t][idx];
    });
    return obj;
  }) || [];

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 font-sans p-8">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Header */}
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">
              PulseGen <span className="text-indigo-600">AI</span>
            </h1>
            <p className="text-slate-500 mt-1">Agentic App Review Trend Analyzer</p>
          </div>

          <div className="flex gap-2">
            {/* Quick Test Button */}
            <button
              onClick={() => setAppName("TEST")}
              className="text-xs font-medium text-slate-400 hover:text-indigo-500 transition px-3 py-1 border rounded-full"
            >
              Load Mock Data
            </button>
          </div>
        </header>

        {/* Search Section */}
        <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col md:flex-row gap-4 items-end">
          <div className="flex-1 w-full space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">App Name</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={appName}
                onChange={e => setAppName(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none transition font-medium"
                placeholder="e.g. Swiggy, Zomato, Instagram..."
              />
            </div>
          </div>

          <div className="w-full md:w-auto space-y-2">
            <label className="text-xs font-bold text-slate-500 uppercase tracking-wider">Analysis Dates</label>
            <div className="flex gap-2">
              <input
                type="date"
                value={dates[0]}
                onChange={e => {
                  const newDates = [...dates];
                  newDates[0] = e.target.value;
                  setDates(newDates);
                }}
                className="px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <span className="self-center text-slate-400">to</span>
              <input
                type="date"
                value={dates[1] || ''}
                onChange={e => {
                  const newDates = [...dates];
                  newDates[1] = e.target.value;
                  setDates(newDates);
                }}
                className="px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full md:w-auto px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-xl shadow-lg shadow-indigo-200 transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin w-5 h-5" /> : 'Analyze Trends'}
          </button>
        </section>

        {/* Error Message */}
        {error && (
          <div className="p-4 bg-red-50 text-red-600 text-sm font-medium rounded-xl border border-red-100">
            🚨 {error}
          </div>
        )}

        {/* Results Dashboard */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in-up">

            {/* Left Column: Stats & Matrix */}
            <div className="lg:col-span-2 space-y-6">

              {/* Highlight Cards */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-amber-50 p-5 rounded-xl border border-amber-100">
                  <div className="flex items-center gap-2 mb-2">
                    <Zap className="w-5 h-5 text-amber-500" />
                    <h3 className="text-sm font-bold text-amber-900 uppercase">New Topics</h3>
                  </div>
                  <div className="space-y-1">
                    {result.newTopics.length > 0 ? (
                      result.newTopics.map(t => (
                        <div key={t} className="inline-block px-2 py-1 bg-white rounded-md text-xs font-semibold text-amber-800 border border-amber-200 mr-2 shadow-sm">
                          {t}
                        </div>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400">No new issues detected.</span>
                    )}
                  </div>
                </div>

                <div className="bg-rose-50 p-5 rounded-xl border border-rose-100">
                  <div className="flex items-center gap-2 mb-2">
                    <Flame className="w-5 h-5 text-rose-500" />
                    <h3 className="text-sm font-bold text-rose-900 uppercase">Spikes {'>'} 2x</h3>
                  </div>
                  <div className="space-y-1">
                    {result.spikes.length > 0 ? (
                      result.spikes.map(t => (
                        <div key={t} className="inline-block px-2 py-1 bg-white rounded-md text-xs font-semibold text-rose-800 border border-rose-200 mr-2 shadow-sm">
                          {t}
                        </div>
                      ))
                    ) : (
                      <span className="text-sm text-slate-400">No volume spikes.</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Chart */}
              <TrendChart data={chartData} topics={result.topics} />

              {/* Data Table */}
              <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
                  <h3 className="font-bold text-slate-800">Detailed Breakdown</h3>
                  <button
                    onClick={handleDownloadCSV}
                    className="text-xs text-indigo-600 font-medium hover:underline flex items-center gap-1"
                  >
                    <Download className="w-3 h-3" /> Export CSV
                  </button>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-500 font-semibold">
                      <tr>
                        <th className="px-6 py-3">Topic</th>
                        {result.dates.map(d => <th key={d} className="px-6 py-3 text-right">{d}</th>)}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {result.topics.slice(0, 10).map(topic => (
                        <tr key={topic} className="hover:bg-slate-50/50">
                          <td className="px-6 py-3 font-medium text-slate-700">{topic}</td>
                          {result.dates.map((d, i) => (
                            <td key={d} className="px-6 py-3 text-right font-mono text-slate-600">
                              {result.trend[topic][i] > 0 ? result.trend[topic][i] : '-'}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {result.topics.length > 10 && (
                  <div className="px-6 py-3 text-center text-xs text-slate-400 bg-slate-50 border-t border-slate-100">
                    Showing top 10 of {result.topics.length} topics
                  </div>
                )}
              </div>
            </div>

            {/* Right Column: Insights */}
            <div className="lg:col-span-1">
              <InsightPanel text={result.insights} />
            </div>

          </div>
        )}
      </div>
    </main>
  );
}
