import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { incidentService } from '../services/incidentService';
import type { Incident, IncidentGroup } from '../types/incident';
import { Card } from '../components/ui/Card';
import { AlertTriangle, ShieldOff, Search, Zap, Activity, RefreshCw } from 'lucide-react';
import { useJobStatus } from '@/hooks/useJobStatus';
import { JobStatusBadge } from '@/components/ui/JobStatusBadge';

const SEVERITY_COLORS: Record<string, string> = {
    CRITICAL: 'bg-red-100 text-red-800 border-red-200',
    HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
    MEDIUM: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    LOW: 'bg-blue-100 text-blue-800 border-blue-200',
};

const STATUS_COLORS: Record<string, string> = {
    OPEN: 'bg-red-50 text-red-700',
    INVESTIGATING: 'bg-orange-50 text-orange-700',
    REPRODUCED: 'bg-purple-50 text-purple-700',
    RESOLVED: 'bg-green-50 text-green-700',
    CLOSED: 'bg-white/40 backdrop-blur-md text-slate-600',
};

export function IncidentDashboardPage() {
    const navigate = useNavigate();
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [groups, setGroups] = useState<IncidentGroup[]>([]);
    const [jobId, setJobId] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        try {
            const [incRes, grpRes] = await Promise.all([
                incidentService.listIncidents(),
                incidentService.listGroups()
            ]);
            setIncidents(incRes.items);
            setGroups(grpRes.items);
        } catch (e) { console.error(e); }
        finally { setLoading(false); }
    };

    useEffect(() => { void loadData(); }, []);

    const { data: job } = useJobStatus(jobId, {
        onComplete: () => {
            void loadData();
            setTimeout(() => setJobId(null), 5000);
        }
    });

    const handleDetect = async () => {
        try {
            const res = await incidentService.detectIncidents();
            setJobId(res.job_id);
        } catch (e) { console.error(e); }
    };

    const detecting = job && job.status !== 'COMPLETED' && job.status !== 'FAILED';

    const total = incidents.length;
    const open = incidents.filter(i => i.status === 'OPEN').length;
    const critical = incidents.filter(i => i.severity === 'CRITICAL').length;
    const reproducible = incidents.filter(i => i.reproducible).length;
    const regCandidates = incidents.filter(i => i.regression_candidate).length;

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Incident Intelligence</h1>
                    <p className="text-slate-500 mt-1">Automated incident capture, classification, and reproduction from Phase 3 failures.</p>
                </div>
                <div className="flex items-center gap-4">
                    {job && <JobStatusBadge status={job.status} elapsed={job.elapsed_seconds} />}
                    <button
                        onClick={() => { void handleDetect(); }}
                        disabled={!!detecting}
                        className="flex items-center gap-2 px-5 py-2.5 glass-dark-button rounded-lg disabled:opacity-50 transition font-medium"
                    >
                        {detecting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                        {detecting ? 'Detecting...' : 'Auto Detect'}
                    </button>
                </div>
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                {[
                    { label: 'Total', value: total, icon: Activity, color: 'text-slate-700' },
                    { label: 'Open', value: open, icon: AlertTriangle, color: 'text-red-600' },
                    { label: 'Critical', value: critical, icon: ShieldOff, color: 'text-red-700' },
                    { label: 'Reproducible', value: reproducible, icon: RefreshCw, color: 'text-purple-600' },
                    { label: 'Regression Candidates', value: regCandidates, icon: Zap, color: 'text-green-600' },
                ].map(m => (
                    <Card key={m.label} className="p-4 flex items-center gap-3">
                        <m.icon className={`w-6 h-6 ${m.color} flex-shrink-0`} />
                        <div>
                            <div className="text-xs text-slate-500 font-medium">{m.label}</div>
                            <div className="text-2xl font-bold">{loading ? '—' : m.value}</div>
                        </div>
                    </Card>
                ))}
            </div>

            {/* Incident Table */}
            <Card className="overflow-hidden">
                <div className="px-6 py-4 border-b flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Incidents</h2>
                    <span className="text-sm text-slate-500">{incidents.length} total</span>
                </div>
                {loading ? (
                    <div className="p-12 text-center text-slate-400 animate-pulse">Loading incidents...</div>
                ) : incidents.length === 0 ? (
                    <div className="p-12 text-center">
                        <ShieldOff className="w-12 h-12 mx-auto text-slate-200 mb-3" />
                        <p className="text-slate-500 font-medium">No incidents detected</p>
                        <p className="text-slate-400 text-sm mt-1">Run Phase 3 scenarios then click Auto Detect.</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="bg-white/40 backdrop-blur-md border-b text-slate-600">
                                <tr>
                                    <th className="px-5 py-3 font-medium">Incident</th>
                                    <th className="px-5 py-3 font-medium">Severity</th>
                                    <th className="px-5 py-3 font-medium">Category</th>
                                    <th className="px-5 py-3 font-medium">Failure Type</th>
                                    <th className="px-5 py-3 font-medium">Status</th>
                                    <th className="px-5 py-3 font-medium">Reproducible</th>
                                    <th className="px-5 py-3 font-medium">Regression</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y">
                                {incidents.map(inc => (
                                    <tr
                                        key={inc.id}
                                        className="hover:bg-white/40 backdrop-blur-md cursor-pointer"
                                        onClick={() => navigate(`/incidents/${inc.incident_id}`)}
                                    >
                                        <td className="px-5 py-3">
                                            <div className="font-mono font-semibold text-slate-800">{inc.incident_id}</div>
                                            <div className="text-xs text-slate-400 truncate max-w-[200px]">{inc.title}</div>
                                        </td>
                                        <td className="px-5 py-3">
                                            <span className={`text-xs font-medium px-2 py-1 rounded border ${SEVERITY_COLORS[inc.severity] ?? 'bg-white/50 backdrop-blur-lg text-slate-600'}`}>
                                                {inc.severity}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 font-mono text-xs text-slate-600">{inc.category}</td>
                                        <td className="px-5 py-3 font-mono text-xs text-slate-600">{inc.failure_type}</td>
                                        <td className="px-5 py-3">
                                            <span className={`text-xs font-medium px-2 py-1 rounded ${STATUS_COLORS[inc.status] ?? 'bg-white/50 backdrop-blur-lg text-slate-600'}`}>
                                                {inc.status}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 text-center">{inc.reproducible ? '✅' : '—'}</td>
                                        <td className="px-5 py-3 text-center">{inc.regression_candidate ? '✅' : '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Card>

            {/* Incident Groups */}
            {groups.length > 0 && (
                <Card className="overflow-hidden">
                    <div className="px-6 py-4 border-b">
                        <h2 className="text-lg font-semibold">Incident Groups</h2>
                        <p className="text-sm text-slate-500">Identical failures grouped by fingerprint.</p>
                    </div>
                    <div className="divide-y">
                        {groups.map(g => (
                            <div key={g.id} className="px-6 py-4 flex items-center justify-between">
                                <div>
                                    <div className="font-mono text-sm font-medium">{g.category} / {g.failure_type}</div>
                                    <div className="text-xs text-slate-400 font-mono">{g.group_key.slice(0, 16)}...</div>
                                </div>
                                <div className="flex items-center gap-6 text-sm">
                                    <div className="text-slate-500"><span className="font-bold text-slate-800">{g.occurrence_count}</span> occurrences</div>
                                    <span className={`text-xs font-medium px-2 py-1 rounded ${STATUS_COLORS[g.status] ?? 'bg-slate-100'}`}>{g.status}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </Card>
            )}
        </div>
    );
}
