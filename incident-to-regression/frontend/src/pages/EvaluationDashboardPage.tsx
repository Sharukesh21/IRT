import { useState, useEffect } from 'react';
import { evaluationService } from '../services/evaluationService';
import type { EvaluationBenchmark, EvaluationMetrics } from '../types/evaluation';
import { Card } from '../components/ui/Card';
import { Activity, Beaker, PlayCircle, Loader2, Target, BarChart2 } from 'lucide-react';

export function EvaluationDashboardPage() {
    const [benchmarks, setBenchmarks] = useState<EvaluationBenchmark[]>([]);
    const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
    const [loading, setLoading] = useState(false);
    const [runningBenchmark, setRunningBenchmark] = useState<string | null>(null);

    const loadData = async () => {
        try {
            const [bRes, mRes] = await Promise.all([
                evaluationService.listBenchmarks(),
                evaluationService.getMetrics()
            ]);
            setBenchmarks(bRes.items);
            setMetrics(mRes);
        } catch (e) {
            console.error('Failed to load evaluation data', e);
        }
    };

    useEffect(() => {
        void loadData();
    }, []);

    const handleSeed = async () => {
        setLoading(true);
        await evaluationService.seedBenchmarks();
        await loadData();
        setLoading(false);
    };

    const handleRunBenchmark = async (benchmarkId: string) => {
        setRunningBenchmark(benchmarkId);
        try {
            await evaluationService.runExperiment(benchmarkId);
            await loadData();
        } catch (e) {
            console.error(e);
        } finally {
            setRunningBenchmark(null);
        }
    };

    const formatPct = (val?: number) => val !== undefined ? `${val.toFixed(1)}%` : '—';

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold flex items-center gap-3">
                        <Target className="w-8 h-8 text-blue-600" /> Evaluation Center
                    </h1>
                    <p className="text-slate-500 mt-1">Final Capstone validation, benchmarking, and metrics.</p>
                </div>
                <button 
                    onClick={() => { void handleSeed(); }} 
                    disabled={loading}
                    className="px-4 py-2 glass-dark-button rounded font-medium disabled:opacity-50 flex items-center gap-2"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Beaker className="w-4 h-4" />}
                    Seed Benchmarks
                </button>
            </div>

            {/* Metrics Dashboard */}
            <Card className="p-6">
                <h2 className="font-semibold mb-6 flex items-center gap-2 text-lg"><BarChart2 className="w-5 h-5 text-blue-500" /> Pipeline Evaluation Metrics</h2>
                
                {metrics?.status === 'INSUFFICIENT DATA' ? (
                    <div className="p-8 text-center text-slate-500 bg-white/40 backdrop-blur-md rounded-lg border border-slate-200 border-dashed">
                        INSUFFICIENT DATA. Run experiments to generate metrics.
                    </div>
                ) : (
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        <div className="p-4 border-l-4 border-slate-500 bg-white/40 backdrop-blur-md rounded">
                            <div className="text-xs text-slate-500 font-medium uppercase mb-1">Total Experiments</div>
                            <div className="text-2xl font-bold">{metrics?.total_experiments ?? 0}</div>
                        </div>
                        <div className="p-4 border-l-4 border-blue-500 bg-white/40 backdrop-blur-md rounded">
                            <div className="text-xs text-slate-500 font-medium uppercase mb-1">Detection Rate</div>
                            <div className="text-2xl font-bold text-blue-700">{formatPct(metrics?.detection_rate)}</div>
                        </div>
                        <div className="p-4 border-l-4 border-indigo-500 bg-white/40 backdrop-blur-md rounded">
                            <div className="text-xs text-slate-500 font-medium uppercase mb-1">Reproduction Rate</div>
                            <div className="text-2xl font-bold text-indigo-700">{formatPct(metrics?.reproduction_rate)}</div>
                        </div>
                        <div className="p-4 border-l-4 border-purple-500 bg-white/40 backdrop-blur-md rounded">
                            <div className="text-xs text-slate-500 font-medium uppercase mb-1">Test Gen Rate</div>
                            <div className="text-2xl font-bold text-purple-700">{formatPct(metrics?.test_generation_rate)}</div>
                        </div>
                        <div className="p-4 border-l-4 border-green-500 bg-green-50 rounded">
                            <div className="text-xs text-green-700 font-medium uppercase mb-1">End-to-End Conversion</div>
                            <div className="text-2xl font-bold text-green-700">{formatPct(metrics?.end_to_end_conversion_rate)}</div>
                        </div>
                    </div>
                )}
            </Card>

            {/* Benchmarks List */}
            <Card className="overflow-hidden">
                <div className="px-6 py-4 border-b bg-white/40 backdrop-blur-md">
                    <h2 className="font-semibold text-lg flex items-center gap-2"><Activity className="w-5 h-5 text-indigo-500" /> Benchmark Dataset</h2>
                </div>
                <div className="overflow-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-white/40 backdrop-blur-md text-xs text-slate-500 uppercase tracking-wider">
                            <tr>
                                <th className="px-6 py-4 text-left font-semibold">ID</th>
                                <th className="px-6 py-4 text-left font-semibold">Scenario</th>
                                <th className="px-6 py-4 text-left font-semibold">Category</th>
                                <th className="px-6 py-4 text-left font-semibold">Severity</th>
                                <th className="px-6 py-4 text-right font-semibold">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {benchmarks.map(b => (
                                <tr key={b.id} className="hover:bg-white/40 backdrop-blur-md transition-colors">
                                    <td className="px-6 py-4 font-mono text-xs font-semibold text-slate-600">{b.benchmark_id}</td>
                                    <td className="px-6 py-4">
                                        <div className="font-medium text-slate-900">{b.scenario_name}</div>
                                        <div className="text-xs text-slate-500 mt-1">{b.description}</div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="px-2.5 py-1 bg-white/50 backdrop-blur-lg text-slate-600 text-xs rounded font-medium">{b.category}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 text-xs rounded font-bold ${
                                            b.severity === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                                            b.severity === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                                            b.severity === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                                            'bg-blue-100 text-blue-700'
                                        }`}>
                                            {b.severity}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button
                                            onClick={() => { void handleRunBenchmark(b.benchmark_id); }}
                                            disabled={runningBenchmark !== null}
                                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 rounded text-xs font-medium transition-colors disabled:opacity-50"
                                        >
                                            {runningBenchmark === b.benchmark_id ? (
                                                <Loader2 className="w-4 h-4 animate-spin" />
                                            ) : (
                                                <PlayCircle className="w-4 h-4" />
                                            )}
                                            {runningBenchmark === b.benchmark_id ? 'Running...' : 'Run Pipeline'}
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {benchmarks.length === 0 && (
                                <tr>
                                    <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                                        No benchmarks loaded. Click "Seed Benchmarks" to initialize the dataset.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
