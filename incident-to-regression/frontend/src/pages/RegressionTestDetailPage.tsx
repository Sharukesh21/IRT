import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { regressionService } from '../services/regressionService';
import type { RegressionTest, RegressionTestRun, RegressionProof } from '../types/regression';
import { Card } from '../components/ui/Card';
import { ArrowLeft, Play, RefreshCw, CheckCircle2, ShieldAlert, FileCode2, History, ArrowRight } from 'lucide-react';
import { useJobStatus } from '@/hooks/useJobStatus';
import { JobStatusBadge } from '@/components/ui/JobStatusBadge';

export function RegressionTestDetailPage() {
    const { testId = '' } = useParams<{ testId: string }>();
    const navigate = useNavigate();
    const [test, setTest] = useState<RegressionTest | null>(null);
    const [proof, setProof] = useState<RegressionProof | null>(null);
    const [runs, setRuns] = useState<RegressionTestRun[]>([]);
    const [loading, setLoading] = useState(true);
    const [jobId, setJobId] = useState<string | null>(null);

    const load = useCallback(async () => {
        try {
            const data = await regressionService.getTest(testId);
            setTest(data.test);
            setProof(data.proof);
            setRuns(data.runs);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    }, [testId]);

    useEffect(() => { void load(); }, [load]);

    const { data: job } = useJobStatus(jobId, {
        onComplete: () => {
            void load();
            setTimeout(() => setJobId(null), 5000);
        }
    });

    const handleRun = async () => {
        try {
            const res = await regressionService.runTest(testId);
            setJobId(res.job_id);
        } catch (e) { console.error(e); }
    };

    if (loading) return <div className="p-12 text-center text-slate-400 animate-pulse">Loading test...</div>;
    if (!test) return <div className="p-12 text-center text-red-500">Test not found.</div>;

    const latestRun = runs.length > 0 ? runs[0] : null;
    const running = job && job.status !== 'COMPLETED' && job.status !== 'FAILED';

    // Type casting for definition
    const def = test.test_definition as { 
        initial_state?: string;
        events?: Record<string, unknown>[];
        failure?: { type: string; target: string };
        assertions?: { path: string; operator: string; expected: unknown }[];
    };

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-6">
            <button onClick={() => navigate('/regression')} className="flex items-center gap-2 text-slate-500 hover:text-slate-800 text-sm">
                <ArrowLeft className="w-4 h-4" /> Back to Regression Center
            </button>

            <div className="flex items-start justify-between gap-4">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <span className="text-xs font-mono bg-white/50 backdrop-blur-lg text-slate-600 px-3 py-1 rounded-full">{test.test_id}</span>
                        <span className="text-xs font-bold px-2 py-1 rounded bg-blue-100 text-blue-800">v{test.version}</span>
                        <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">{test.status}</span>
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900">{test.name}</h1>
                    <p className="text-slate-500 text-sm mt-1">{test.description}</p>
                </div>
                <div className="flex items-center gap-4">
                    {job && <JobStatusBadge status={job.status} elapsed={job.elapsed_seconds} />}
                    <button
                        onClick={() => { void handleRun(); }}
                        disabled={!!running}
                        className="flex items-center gap-2 px-6 py-2.5 glass-dark-button rounded-lg font-medium disabled:opacity-50"
                    >
                        {running ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                        {running ? 'Executing...' : 'Run Test'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Proof Panel */}
                {proof && proof.before_status && (
                    <Card className={`p-5 md:col-span-3 border-2 ${proof.protected ? 'border-green-400 bg-green-50' : 'border-slate-200'}`}>
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className={`font-bold flex items-center gap-2 ${proof.protected ? 'text-green-800' : 'text-slate-700'}`}>
                                    {proof.protected ? <CheckCircle2 className="w-5 h-5" /> : <ShieldAlert className="w-5 h-5" />}
                                    {proof.protected ? 'REGRESSION PROTECTED' : 'REGRESSION PROOF STATUS'}
                                </h3>
                                <p className="text-sm mt-1 text-slate-600">
                                    {proof.protected
                                        ? 'This test successfully failed before the fix and passed after the fix, proving the application is protected.'
                                        : 'Test has not yet demonstrated a transition from FAIL to PASS.'}
                                </p>
                            </div>
                            <div className="flex gap-4 font-mono text-sm">
                                <div className="text-center">
                                    <div className="text-xs text-slate-500 mb-1">Before Fix</div>
                                    <div className={`font-bold ${proof.before_status === 'FAILED' ? 'text-red-600' : 'text-slate-600'}`}>{proof.before_status}</div>
                                </div>
                                <ArrowRight className="w-4 h-4 mt-4 text-slate-300" />
                                <div className="text-center">
                                    <div className="text-xs text-slate-500 mb-1">After Fix</div>
                                    <div className={`font-bold ${proof.after_status === 'PASSED' ? 'text-green-600' : 'text-slate-600'}`}>{proof.after_status || 'PENDING'}</div>
                                </div>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Left Col: Definition */}
                <div className="md:col-span-2 space-y-6">
                    <Card className="p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><FileCode2 className="w-5 h-5 text-slate-500" /> Test Definition</h2>
                        
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Initial State</h3>
                                <div className="font-mono text-sm bg-white/40 backdrop-blur-md p-3 rounded border">{String(def.initial_state || '')}</div>
                            </div>

                            <div>
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Event Sequence</h3>
                                <div className="space-y-2">
                                    {Array.isArray(def.events) && def.events.map((e, i) => (
                                        <div key={i} className="font-mono text-sm bg-white/40 backdrop-blur-md p-3 rounded border flex items-center gap-3">
                                            <span className="text-slate-400">{String(i + 1).padStart(2, '0')}</span>
                                            <span className="font-semibold text-slate-700">{String(e.type)}</span>
                                            {Object.entries(e).filter(([k]) => k !== 'type').map(([k, v]) => (
                                                <span key={k} className="text-xs text-slate-500">{k}: {String(v)}</span>
                                            ))}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {def.failure && (
                                <div>
                                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Failure Configuration</h3>
                                    <div className="font-mono text-sm bg-red-50 text-red-800 p-3 rounded border border-red-200">
                                        <div><span className="font-semibold">Type:</span> {def.failure.type}</div>
                                        <div><span className="font-semibold">Target:</span> {def.failure.target}</div>
                                    </div>
                                </div>
                            )}

                            <div>
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Assertions</h3>
                                <div className="space-y-2">
                                    {Array.isArray(def.assertions) && def.assertions.map((a, i) => (
                                        <div key={i} className="font-mono text-sm bg-blue-50 text-blue-900 p-3 rounded border border-blue-200 flex items-center gap-2">
                                            <span className="font-bold">ASSERT</span>
                                            <span>{a.path}</span>
                                            <span className="font-bold text-blue-600">{a.operator}</span>
                                            <span>{String(a.expected)}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Latest Trace if available */}
                    {latestRun && latestRun.execution_trace && (
                        <Card className="p-6">
                            <h2 className="text-lg font-semibold mb-4">Latest Execution Trace</h2>
                            <div className="space-y-1">
                                {latestRun.execution_trace.map((step: any, i: number) => (
                                    <div key={i} className="font-mono text-xs flex items-center gap-3 py-1.5 border-b border-slate-100 last:border-0">
                                        <span className="text-slate-400 w-6">[{i + 1}]</span>
                                        <span className="font-semibold">{String(step.event)}</span>
                                        <span className={step.status === 'PROCESSED' ? 'text-green-600' : 'text-red-600'}>{String(step.status)}</span>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    )}
                </div>

                {/* Right Col: Runs */}
                <div className="space-y-6">
                    <Card className="p-6">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><History className="w-5 h-5 text-slate-500" /> Run History</h2>
                        <div className="space-y-3">
                            {runs.map(run => (
                                <div key={run.id} className="p-3 border rounded-lg glass shadow-sm flex flex-col gap-2">
                                    <div className="flex items-center justify-between">
                                        <div className="font-mono text-xs text-slate-500">{run.run_id}</div>
                                        <div className={`text-xs font-bold px-2 py-0.5 rounded ${run.status === 'PASSED' ? 'bg-green-100 text-green-700' : run.status === 'FAILED' ? 'bg-red-100 text-red-700' : 'bg-white/50 backdrop-blur-lg text-slate-700'}`}>
                                            {run.status}
                                        </div>
                                    </div>
                                    <div className="text-xs text-slate-500">
                                        {new Date(run.started_at).toLocaleString()} · {run.duration_ms?.toFixed(0) || 0}ms
                                    </div>
                                    <div className="flex gap-2 text-xs font-mono mt-1">
                                        <span className="text-green-600">{run.assertions_passed} pass</span>
                                        <span className="text-red-600">{run.assertions_failed} fail</span>
                                    </div>
                                </div>
                            ))}
                            {runs.length === 0 && <div className="text-sm text-slate-400">No runs recorded yet.</div>}
                        </div>
                    </Card>
                </div>
            </div>
        </div>
    );
}
