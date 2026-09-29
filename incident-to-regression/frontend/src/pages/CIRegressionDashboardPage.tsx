import { useState, useEffect } from 'react';
import { ciService } from '../services/ciService';
import type { CIMetrics, RegressionOrchestration, CIRegressionRun, RegressionEscape } from '../types/ci';
import { Card } from '../components/ui/Card';
import { Shield, ShieldCheck, ShieldAlert, Activity, Zap, PlayCircle, GitBranch, RefreshCw, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

export function CIRegressionDashboardPage() {
    const [metrics, setMetrics] = useState<CIMetrics | null>(null);
    const [orchestrations, setOrchestrations] = useState<RegressionOrchestration[]>([]);
    const [ciRuns, setCiRuns] = useState<CIRegressionRun[]>([]);
    const [escapes, setEscapes] = useState<RegressionEscape[]>([]);
    const [running, setRunning] = useState(false);
    const [ciForm, setCiForm] = useState({ incident_id: '', strategy: 'TARGETED', branch: '', commit_sha: '' });
    const [ciResult, setCiResult] = useState<{ status: string; tests: number; passed: number; failed: number } | null>(null);

    const load = async () => {
        const [m, o, r, e] = await Promise.all([
            ciService.getMetrics(),
            ciService.listOrchestrations(),
            ciService.listCIRuns(),
            ciService.listEscapes()
        ]);
        setMetrics(m);
        setOrchestrations(o.items);
        setCiRuns(r.items);
        setEscapes(e.items);
    };

    useEffect(() => { void load(); }, []);

    const handleRun = async () => {
        if (!ciForm.incident_id) return;
        setRunning(true);
        setCiResult(null);
        try {
            const res = await ciService.triggerCIRun({ ...ciForm });
            setCiResult(res);
            await load();
        } catch (e) { console.error(e); }
        finally { setRunning(false); }
    };

    const statusBadge = (status: string) => {
        const color = status === 'PASSED' ? 'bg-green-100 text-green-700' : status === 'FAILED' ? 'bg-red-100 text-red-700' : status === 'ERROR' ? 'bg-orange-100 text-orange-700' : 'bg-white/50 backdrop-blur-lg text-slate-700';
        const icon = status === 'PASSED' ? <CheckCircle2 className="w-3 h-3" /> : status === 'FAILED' ? <XCircle className="w-3 h-3" /> : status === 'ERROR' ? <AlertTriangle className="w-3 h-3" /> : null;
        return <span className={`inline-flex items-center gap-1 text-xs font-bold px-2 py-0.5 rounded ${color}`}>{icon}{status}</span>;
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">CI Regression Dashboard</h1>
                    <p className="text-slate-500 mt-1">Incident-aware automated regression status across all code changes.</p>
                </div>
                <button onClick={() => { void load(); }} className="p-2 rounded hover:bg-white/50 backdrop-blur-lg">
                    <RefreshCw className="w-4 h-4 text-slate-500" />
                </button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                    { label: 'Incidents', value: metrics?.incidents_total ?? 0, icon: <Activity className="w-5 h-5 text-blue-500" />, border: 'border-l-blue-500' },
                    { label: 'Tests', value: metrics?.tests_total ?? 0, icon: <Shield className="w-5 h-5 text-slate-500" />, border: 'border-l-slate-500' },
                    { label: 'Externally Ingested', value: metrics?.external_ingested ?? 0, icon: <Zap className="w-5 h-5 text-orange-500" />, border: 'border-l-orange-500' },
                    { label: 'Regression Escapes', value: metrics?.escapes_total ?? 0, icon: <ShieldAlert className="w-5 h-5 text-red-500" />, border: 'border-l-red-500' },
                    { label: 'CI Pass Rate', value: `${metrics?.ci_pass_rate ?? 0}%`, icon: <ShieldCheck className="w-5 h-5 text-green-500" />, border: 'border-l-green-500' },
                ].map(m => (
                    <Card key={m.label} className={`p-5 border-l-4 ${m.border} flex items-center gap-3`}>
                        {m.icon}
                        <div>
                            <div className="text-xs text-slate-500">{m.label}</div>
                            <div className="text-xl font-bold">{m.value}</div>
                        </div>
                    </Card>
                ))}
            </div>

            {/* CI Trigger */}
            <Card className="p-6">
                <h2 className="font-semibold mb-4 flex items-center gap-2"><PlayCircle className="w-5 h-5 text-slate-500" /> Trigger CI Regression Run</h2>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                    <div>
                        <label className="text-xs font-medium text-slate-500 block mb-1">Incident ID *</label>
                        <input
                            value={ciForm.incident_id}
                            onChange={e => setCiForm(f => ({ ...f, incident_id: e.target.value }))}
                            placeholder="INC-..."
                            className="w-full px-3 py-2 border rounded text-sm"
                        />
                    </div>
                    <div>
                        <label className="text-xs font-medium text-slate-500 block mb-1">Strategy</label>
                        <select
                            value={ciForm.strategy}
                            onChange={e => setCiForm(f => ({ ...f, strategy: e.target.value }))}
                            className="w-full px-3 py-2 border rounded text-sm"
                        >
                            <option value="TARGETED">TARGETED</option>
                            <option value="FULL">FULL</option>
                        </select>
                    </div>
                    <div>
                        <label className="text-xs font-medium text-slate-500 block mb-1">Branch</label>
                        <input
                            value={ciForm.branch}
                            onChange={e => setCiForm(f => ({ ...f, branch: e.target.value }))}
                            placeholder="feature/fix"
                            className="w-full px-3 py-2 border rounded text-sm"
                        />
                    </div>
                    <div>
                        <label className="text-xs font-medium text-slate-500 block mb-1">Commit SHA</label>
                        <input
                            value={ciForm.commit_sha}
                            onChange={e => setCiForm(f => ({ ...f, commit_sha: e.target.value }))}
                            placeholder="abc123"
                            className="w-full px-3 py-2 border rounded text-sm"
                        />
                    </div>
                </div>
                <button
                    onClick={() => { void handleRun(); }}
                    disabled={running || !ciForm.incident_id}
                    className="flex items-center gap-2 px-5 py-2.5 glass-dark-button rounded-lg font-medium disabled:opacity-50"
                >
                    {running ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlayCircle className="w-4 h-4" />}
                    {running ? 'Running...' : 'Run CI Regression'}
                </button>

                {ciResult && (
                    <div className={`mt-4 p-4 rounded-lg border-2 ${ciResult.status === 'PASSED' ? 'bg-green-50 border-green-400' : 'bg-red-50 border-red-400'}`}>
                        <div className={`font-bold text-lg ${ciResult.status === 'PASSED' ? 'text-green-800' : 'text-red-800'}`}>
                            CI STATUS: {ciResult.status}
                        </div>
                        <div className="mt-2 text-sm flex gap-6 font-mono">
                            <span>Tests: {ciResult.tests}</span>
                            <span className="text-green-700">Passed: {ciResult.passed}</span>
                            <span className="text-red-700">Failed: {ciResult.failed}</span>
                        </div>
                    </div>
                )}
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Orchestrations */}
                <Card className="overflow-hidden">
                    <div className="px-5 py-4 border-b bg-white/40 backdrop-blur-md">
                        <h2 className="font-semibold flex items-center gap-2"><GitBranch className="w-4 h-4" /> Recent Orchestrations</h2>
                    </div>
                    <div className="divide-y max-h-80 overflow-auto">
                        {orchestrations.map(o => (
                            <div key={o.id} className="px-5 py-3 flex items-center justify-between">
                                <div>
                                    <div className="font-mono text-xs font-semibold">{o.orchestration_id}</div>
                                    <div className="text-xs text-slate-500 mt-0.5">{o.trigger_source} · {o.total_tests} tests</div>
                                </div>
                                <div className="flex items-center gap-2 text-xs font-mono">
                                    <span className="text-green-600">{o.passed}P</span>
                                    <span className="text-red-600">{o.failed}F</span>
                                    {statusBadge(o.status)}
                                </div>
                            </div>
                        ))}
                        {orchestrations.length === 0 && <div className="p-8 text-center text-slate-400 text-sm">No orchestrations yet.</div>}
                    </div>
                </Card>

                {/* Regression Escapes */}
                <Card className="overflow-hidden">
                    <div className="px-5 py-4 border-b bg-white/40 backdrop-blur-md">
                        <h2 className="font-semibold flex items-center gap-2"><ShieldAlert className="w-4 h-4 text-red-500" /> Regression Escapes</h2>
                    </div>
                    <div className="divide-y max-h-80 overflow-auto">
                        {escapes.map(e => (
                            <div key={e.id} className="px-5 py-3">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="font-mono text-xs font-semibold text-red-700">ESCAPE DETECTED</span>
                                    <span className="text-xs text-slate-500">{new Date(e.detected_at).toLocaleString()}</span>
                                </div>
                                <div className="text-xs text-slate-600">{e.explanation}</div>
                            </div>
                        ))}
                        {escapes.length === 0 && (
                            <div className="p-8 text-center text-green-600 text-sm flex flex-col items-center gap-2">
                                <ShieldCheck className="w-8 h-8" />
                                No regression escapes detected.
                            </div>
                        )}
                    </div>
                </Card>
            </div>

            {/* CI Run History */}
            <Card className="overflow-hidden">
                <div className="px-6 py-4 border-b bg-white/40 backdrop-blur-md">
                    <h2 className="font-semibold">CI Run History</h2>
                </div>
                <div className="overflow-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-white/40 backdrop-blur-md text-xs text-slate-500 uppercase tracking-wider">
                            <tr>
                                {['Run ID', 'Branch', 'Commit', 'PR', 'Status', 'Started'].map(h => (
                                    <th key={h} className="px-4 py-3 text-left font-semibold">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {ciRuns.map(r => (
                                <tr key={r.id} className="hover:bg-white/40 backdrop-blur-md">
                                    <td className="px-4 py-3 font-mono text-xs font-semibold">{r.run_id}</td>
                                    <td className="px-4 py-3 font-mono text-xs">{r.branch || '—'}</td>
                                    <td className="px-4 py-3 font-mono text-xs">{r.commit_sha ? r.commit_sha.slice(0, 7) : '—'}</td>
                                    <td className="px-4 py-3 text-xs">{r.pull_request_number ? `#${r.pull_request_number}` : '—'}</td>
                                    <td className="px-4 py-3">{statusBadge(r.status ?? '')}</td>
                                    <td className="px-4 py-3 text-xs text-slate-500">{new Date(r.started_at).toLocaleString()}</td>
                                </tr>
                            ))}
                            {ciRuns.length === 0 && (
                                <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-400">No CI runs yet.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
