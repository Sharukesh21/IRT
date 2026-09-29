import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { regressionService } from '../services/regressionService';
import type { RegressionTest, RegressionCandidate } from '../types/regression';
import { Card } from '../components/ui/Card';
import { Play, Shield, ShieldCheck, Zap, Activity, ArrowRight, RefreshCw } from 'lucide-react';
import { useJobStatus } from '@/hooks/useJobStatus';
import { JobStatusBadge } from '@/components/ui/JobStatusBadge';

export function RegressionCenterPage() {
    const navigate = useNavigate();
    const [tests, setTests] = useState<RegressionTest[]>([]);
    const [candidates, setCandidates] = useState<RegressionCandidate[]>([]);
    const [metrics, setMetrics] = useState({ total_tests: 0, total_runs: 0, pass_rate: 0 });
    const [jobId, setJobId] = useState<string | null>(null);
    const [generating, setGenerating] = useState<string | null>(null);

    const loadData = async () => {
        try {
            const [testRes, candRes, metRes] = await Promise.all([
                regressionService.listTests(),
                regressionService.listCandidates(),
                regressionService.getMetrics()
            ]);
            setTests(testRes.items);
            setCandidates(candRes.items);
            setMetrics(metRes);
        } catch (e) { console.error(e); }
    };

    useEffect(() => { void loadData(); }, []);

    const { data: job } = useJobStatus(jobId, {
        onComplete: () => {
            void loadData();
            setTimeout(() => setJobId(null), 5000);
        }
    });

    const handleRunSuite = async () => {
        try {
            const res = await regressionService.runSuite();
            setJobId(res.job_id);
        } catch (e) { console.error(e); }
    };

    const suiteRunning = job && job.status !== 'COMPLETED' && job.status !== 'FAILED';

    const handleGenerate = async (candidateId: string) => {
        setGenerating(candidateId);
        try {
            await regressionService.generateTest(candidateId);
            await loadData();
        } catch (e) { console.error(e); }
        finally { setGenerating(null); }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Regression Center</h1>
                    <p className="text-slate-500 mt-1">Automated test generation and execution to protect against recurrence.</p>
                </div>
                <div className="flex items-center gap-4">
                    {job && <JobStatusBadge status={job.status} elapsed={job.elapsed_seconds} />}
                    <button
                        onClick={() => { void handleRunSuite(); }}
                        disabled={!!suiteRunning || tests.length === 0}
                        className="flex items-center gap-2 px-5 py-2.5 glass-dark-button rounded-lg disabled:opacity-50 font-medium"
                    >
                        {suiteRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                        {suiteRunning ? 'Running Suite...' : 'Run Regression Suite'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="p-5 flex items-center gap-4 border-l-4 border-l-slate-800">
                    <Shield className="w-8 h-8 text-slate-400" />
                    <div>
                        <div className="text-sm font-medium text-slate-500">Active Tests</div>
                        <div className="text-2xl font-bold">{metrics.total_tests}</div>
                    </div>
                </Card>
                <Card className="p-5 flex items-center gap-4 border-l-4 border-l-blue-500">
                    <Activity className="w-8 h-8 text-blue-500" />
                    <div>
                        <div className="text-sm font-medium text-slate-500">Total Executions</div>
                        <div className="text-2xl font-bold">{metrics.total_runs}</div>
                    </div>
                </Card>
                <Card className="p-5 flex items-center gap-4 border-l-4 border-l-green-500">
                    <ShieldCheck className="w-8 h-8 text-green-500" />
                    <div>
                        <div className="text-sm font-medium text-slate-500">Suite Pass Rate</div>
                        <div className="text-2xl font-bold">{metrics.pass_rate.toFixed(1)}%</div>
                    </div>
                </Card>
                <Card className="p-5 flex items-center gap-4 border-l-4 border-l-purple-500">
                    <Zap className="w-8 h-8 text-purple-500" />
                    <div>
                        <div className="text-sm font-medium text-slate-500">Incident Conversion</div>
                        <div className="text-2xl font-bold">{(metrics.total_tests / (candidates.length || 1) * 100).toFixed(0)}%</div>
                    </div>
                </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Candidates */}
                <Card className="overflow-hidden flex flex-col">
                    <div className="px-6 py-4 border-b bg-white/40 backdrop-blur-md">
                        <h2 className="font-semibold flex items-center gap-2"><Zap className="w-4 h-4 text-orange-500" /> Pending Candidates</h2>
                    </div>
                    <div className="flex-1 divide-y overflow-auto max-h-[500px]">
                        {candidates.filter(c => c.status === 'PENDING').map(cand => (
                            <div key={cand.id} className="p-5 hover:bg-white/40 backdrop-blur-md flex justify-between items-start gap-4">
                                <div>
                                    <div className="font-mono text-xs font-semibold text-slate-500 mb-1">{cand.candidate_id}</div>
                                    <div className="font-medium text-sm">{cand.name}</div>
                                    <div className="text-xs text-slate-500 mt-1">{cand.description}</div>
                                </div>
                                <button
                                    onClick={() => { void handleGenerate(cand.candidate_id); }}
                                    disabled={generating === cand.candidate_id}
                                    className="flex-shrink-0 text-xs px-3 py-1.5 bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium rounded border border-blue-200 disabled:opacity-50"
                                >
                                    {generating === cand.candidate_id ? 'Generating...' : 'Generate Test'}
                                </button>
                            </div>
                        ))}
                        {candidates.filter(c => c.status === 'PENDING').length === 0 && (
                            <div className="p-8 text-center text-slate-400 text-sm">No pending candidates. Generate them from incidents.</div>
                        )}
                    </div>
                </Card>

                {/* Tests */}
                <Card className="overflow-hidden flex flex-col">
                    <div className="px-6 py-4 border-b bg-white/40 backdrop-blur-md">
                        <h2 className="font-semibold flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-green-600" /> Active Regression Tests</h2>
                    </div>
                    <div className="flex-1 divide-y overflow-auto max-h-[500px]">
                        {tests.map(test => (
                            <div
                                key={test.id}
                                onClick={() => navigate(`/regression/${test.test_id}`)}
                                className="p-5 hover:bg-white/40 backdrop-blur-md cursor-pointer flex justify-between items-center group"
                            >
                                <div>
                                    <div className="flex items-center gap-2 mb-1">
                                        <span className="font-mono text-xs font-bold text-slate-700">{test.test_id}</span>
                                        <span className="text-[10px] uppercase font-bold bg-green-100 text-green-800 px-1.5 rounded">v{test.version}</span>
                                    </div>
                                    <div className="font-medium text-sm group-hover:text-blue-600 transition-colors">{test.name}</div>
                                </div>
                                <ArrowRight className="w-4 h-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
                            </div>
                        ))}
                        {tests.length === 0 && (
                            <div className="p-8 text-center text-slate-400 text-sm">No tests generated yet.</div>
                        )}
                    </div>
                </Card>
            </div>
        </div>
    );
}
