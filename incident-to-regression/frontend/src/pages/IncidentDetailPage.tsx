import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { incidentService } from '../services/incidentService';
import type { IncidentDetails, IncidentTimeline } from '../types/incident';
import { Card } from '../components/ui/Card';
import {
    AlertTriangle, CheckCircle2, RefreshCw, ArrowLeft,
    Clock, Zap, ShieldAlert, ActivitySquare, ChevronRight
} from 'lucide-react';

const SEVERITY_COLORS: Record<string, string> = {
    CRITICAL: 'bg-red-600 text-white',
    HIGH: 'bg-orange-500 text-white',
    MEDIUM: 'bg-yellow-500 text-white',
    LOW: 'bg-blue-500 text-white',
};

function TimelineItem({ item, isLast }: { item: IncidentTimeline; isLast: boolean }) {
    const isAnomaly = item.is_anomalous;
    return (
        <div className="flex gap-4">
            <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 border-2 ${
                    isAnomaly ? 'border-red-500 bg-red-50 text-red-600' : 'border-slate-300 glass text-slate-500'
                }`}>
                    {isAnomaly ? <AlertTriangle className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </div>
                {!isLast && <div className="w-0.5 h-full bg-slate-200 mt-1" />}
            </div>
            <div className={`pb-6 flex-1 ${isLast ? '' : ''}`}>
                <div className={`text-sm font-semibold font-mono ${isAnomaly ? 'text-red-700' : 'text-slate-700'}`}>
                    {item.event_type}
                    {isAnomaly && <span className="ml-2 text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded">⚠ {item.failure_type}</span>}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                    {new Date(item.occurred_at).toLocaleTimeString()} · Seq #{item.sequence} · {item.processing_status}
                </div>
            </div>
        </div>
    );
}

export function IncidentDetailPage() {
    const { incidentId = '' } = useParams<{ incidentId: string }>();
    const navigate = useNavigate();
    const [details, setDetails] = useState<IncidentDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const [reproducing, setReproducing] = useState(false);
    const [reproResult, setReproResult] = useState<{ match: boolean; original_outcome: string; reproduced_outcome: string } | null>(null);
    const [creatingRC, setCreatingRC] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await incidentService.getIncident(incidentId);
                setDetails(data);
            } catch (e) { console.error(e); }
            finally { setLoading(false); }
        };
        void load();
    }, [incidentId]);

    const handleReproduce = async () => {
        setReproducing(true);
        try {
            const res = await incidentService.reproduce(incidentId);
            setReproResult(res);
        } catch (e) { console.error(e); }
        finally { setReproducing(false); }
    };

    const handleCreateRC = async () => {
        setCreatingRC(true);
        try {
            const res = await incidentService.createRegressionCandidate(incidentId);
            alert(`Regression Candidate created: ${res.candidate_id}`);
            const data = await incidentService.getIncident(incidentId);
            setDetails(data);
        } catch (e) { console.error(e); }
        finally { setCreatingRC(false); }
    };

    if (loading) return <div className="p-12 text-center text-slate-400 animate-pulse">Loading incident...</div>;
    if (!details) return <div className="p-12 text-center text-red-500">Incident not found.</div>;

    const { incident, timeline, expectations, root_cause, reproduction, regression_candidate } = details;

    const expectedEntries = expectations ? Object.entries(expectations.expected_state) : [];
    const actualEntries = expectations ? Object.entries(expectations.actual_state) : [];

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-6">
            {/* Back nav */}
            <button onClick={() => navigate('/incidents')} className="flex items-center gap-2 text-slate-500 hover:text-slate-800 text-sm">
                <ArrowLeft className="w-4 h-4" /> Back to Incidents
            </button>

            {/* Incident Header */}
            <div className="flex items-start justify-between gap-4">
                <div>
                    <div className="flex items-center gap-3 mb-1">
                        <span className="text-xs font-mono bg-white/50 backdrop-blur-lg text-slate-600 px-3 py-1 rounded-full">{incident.incident_id}</span>
                        <span className={`text-xs font-bold px-2 py-1 rounded ${SEVERITY_COLORS[incident.severity] ?? 'bg-slate-200'}`}>
                            {incident.severity}
                        </span>
                        <span className="text-xs px-2 py-1 rounded bg-white/50 backdrop-blur-lg text-slate-600">{incident.status}</span>
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900">{incident.title}</h1>
                    <p className="text-slate-500 text-sm mt-1">{incident.description}</p>
                </div>
                <div className="flex items-center gap-2 flex-shrink-0">
                    {!regression_candidate && (
                        <button
                            onClick={() => { void handleCreateRC(); }}
                            disabled={creatingRC}
                            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-300 text-sm hover:bg-white/40 backdrop-blur-md"
                        >
                            <Zap className="w-4 h-4" />
                            {creatingRC ? 'Creating...' : 'Create Regression Candidate'}
                        </button>
                    )}
                    <button
                        onClick={() => { void handleReproduce(); }}
                        disabled={reproducing}
                        className="flex items-center gap-2 px-4 py-2 glass-dark-button rounded-lg text-sm disabled:opacity-50"
                    >
                        <RefreshCw className={`w-4 h-4 ${reproducing ? 'animate-spin' : ''}`} />
                        {reproducing ? 'Reproducing...' : 'Reproduce Incident'}
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 glass border rounded-lg">
                    <div className="text-xs text-slate-500 mb-1">Category</div>
                    <div className="font-mono font-medium text-sm">{incident.category}</div>
                </div>
                <div className="p-4 glass border rounded-lg">
                    <div className="text-xs text-slate-500 mb-1">Failure Type</div>
                    <div className="font-mono font-medium text-sm">{incident.failure_type}</div>
                </div>
                <div className="p-4 glass border rounded-lg flex items-center gap-2">
                    {incident.state_corrupted
                        ? <><ShieldAlert className="w-5 h-5 text-red-500" /><span className="font-semibold text-red-700 text-sm">STATE CORRUPTED</span></>
                        : <><CheckCircle2 className="w-5 h-5 text-green-500" /><span className="font-semibold text-green-700 text-sm">STATE INTACT</span></>}
                </div>
            </div>

            {/* Reproduction Result */}
            {reproResult && (
                <Card className={`p-5 border-2 ${reproResult.match ? 'border-green-300 bg-green-50' : 'border-red-300 bg-red-50'}`}>
                    <h3 className="font-bold text-lg mb-3">{reproResult.match ? '✅ REPRODUCED SUCCESSFULLY' : '❌ REPRODUCTION MISMATCH'}</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm font-mono">
                        <div><div className="text-slate-500 mb-1">Original Outcome</div><strong>{reproResult.original_outcome}</strong></div>
                        <div><div className="text-slate-500 mb-1">Reproduced Outcome</div><strong>{reproResult.reproduced_outcome}</strong></div>
                    </div>
                </Card>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Timeline */}
                <Card className="p-6">
                    <h2 className="text-lg font-semibold mb-5 flex items-center gap-2"><Clock className="w-5 h-5" /> Event Timeline</h2>
                    {timeline.length === 0 ? (
                        <p className="text-slate-400 text-sm">No timeline events captured.</p>
                    ) : (
                        <div>
                            {timeline.map((item, idx) => (
                                <TimelineItem key={item.id} item={item} isLast={idx === timeline.length - 1} />
                            ))}
                        </div>
                    )}
                </Card>

                {/* Right Column */}
                <div className="space-y-6">
                    {/* Root Cause */}
                    {root_cause && (
                        <Card className="p-6">
                            <h2 className="text-lg font-semibold mb-3 flex items-center gap-2"><ActivitySquare className="w-5 h-5" /> Root Cause</h2>
                            <div className="bg-white/40 backdrop-blur-md border rounded-lg p-4">
                                <div className="font-mono text-sm font-bold text-red-700 mb-2">{root_cause.cause_code}</div>
                                <p className="text-sm text-slate-700 leading-relaxed">{root_cause.explanation}</p>
                                <div className="mt-2 text-xs text-slate-400">Confidence: <strong>{root_cause.confidence}</strong></div>
                            </div>
                        </Card>
                    )}

                    {/* Expected vs Actual */}
                    {expectations && (
                        <Card className="p-6">
                            <h2 className="text-lg font-semibold mb-4">Expected vs Actual</h2>
                            <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                                <div>
                                    <div className="text-green-700 font-bold mb-2 uppercase text-xs">Expected</div>
                                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 space-y-1">
                                        {expectedEntries.map(([k, v]) => (
                                            <div key={k}><span className="text-slate-500">{k}:</span> <strong>{String(v)}</strong></div>
                                        ))}
                                    </div>
                                </div>
                                <div>
                                    <div className="text-red-700 font-bold mb-2 uppercase text-xs">Actual</div>
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 space-y-1">
                                        {actualEntries.map(([k, v]) => (
                                            <div key={k}><span className="text-slate-500">{k}:</span> <strong>{String(v)}</strong></div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                            {expectations.invariant_violations.length > 0 && (
                                <div className="mt-4 space-y-1">
                                    <div className="text-xs font-bold text-red-700 mb-1">Invariant Violations</div>
                                    {expectations.invariant_violations.map((v, i) => (
                                        <div key={i} className="text-xs text-red-600 flex items-start gap-1.5">
                                            <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" /> {v}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </Card>
                    )}

                    {/* Reproduction Spec */}
                    {reproduction && (
                        <Card className="p-6">
                            <h2 className="text-lg font-semibold mb-3">Reproduction Spec</h2>
                            <div className="text-xs font-mono space-y-2 bg-white/40 backdrop-blur-md rounded-lg p-4 border">
                                <div><span className="text-slate-500">ID:</span> {reproduction.reproduction_id}</div>
                                <div><span className="text-slate-500">Initial State:</span> {reproduction.initial_state}</div>
                                <div><span className="text-slate-500">Expected Outcome:</span> <strong className="text-red-700">{reproduction.expected_outcome}</strong></div>
                                {Object.entries(reproduction.failure_configuration).map(([k, v]) => (
                                    <div key={k}><span className="text-slate-500">{k}:</span> {JSON.stringify(v)}</div>
                                ))}
                            </div>
                        </Card>
                    )}

                    {/* Regression Candidate */}
                    {regression_candidate && (
                        <Card className="p-6 bg-green-50 border border-green-200">
                            <h2 className="text-lg font-semibold mb-2 text-green-800 flex items-center gap-2"><Zap className="w-5 h-5" /> Regression Candidate</h2>
                            <div className="font-mono text-xs text-green-700">{regression_candidate.candidate_id}</div>
                            <div className="text-sm text-green-800 mt-1">{regression_candidate.name}</div>
                            <div className="mt-2 text-xs text-green-600">Status: <strong>{regression_candidate.status}</strong> · Phase 5 will convert this into an automated test.</div>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    );
}
