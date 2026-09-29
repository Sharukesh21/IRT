import { useState } from 'react';
import { ciService } from '../services/ciService';
import type { ExternalIncident } from '../types/ci';
import { SAMPLE_INCIDENTS } from '../types/ci';
import { Card } from '../components/ui/Card';
import { Upload, CheckCircle2, Loader2, FlaskConical } from 'lucide-react';

const STATUS_COLORS: Record<string, string> = {
    RECEIVED: 'bg-white/50 backdrop-blur-lg text-slate-700',
    VALIDATED: 'bg-blue-100 text-blue-700',
    NORMALIZED: 'bg-green-100 text-green-700',
    PROCESSED: 'bg-green-100 text-green-700',
    DUPLICATE: 'bg-yellow-100 text-yellow-700',
    REJECTED: 'bg-red-100 text-red-700',
    ERROR: 'bg-red-100 text-red-700'
};

const PIPELINE_STEPS = ['RECEIVED', 'VALIDATED', 'NORMALIZED', 'PROCESSED'];

export function ProductionIncidentsPage() {
    const [jsonInput, setJsonInput] = useState(JSON.stringify(SAMPLE_INCIDENTS[0], null, 2));
    const [ingestResult, setIngestResult] = useState<{ status: string; external_incident_id: string; normalized_incident_id?: string } | null>(null);
    const [history, setHistory] = useState<ExternalIncident[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleIngest = async () => {
        setLoading(true);
        setError(null);
        setIngestResult(null);
        try {
            const payload = JSON.parse(jsonInput) as Record<string, unknown>;
            const result = await ciService.ingestIncident(payload);
            setIngestResult(result);
            // Reload history
            const hist = await ciService.listExternalIncidents();
            setHistory(hist.items);
        } catch (e: unknown) {
            setError(e instanceof Error ? e.message : 'Ingestion failed');
        } finally {
            setLoading(false);
        }
    };

    const loadSample = (idx: number) => {
        setJsonInput(JSON.stringify(SAMPLE_INCIDENTS[idx], null, 2));
        setIngestResult(null);
        setError(null);
    };

    const loadHistory = async () => {
        const hist = await ciService.listExternalIncidents();
        setHistory(hist.items);
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Incident Ingestion Lab</h1>
                <p className="text-slate-500 mt-1">Simulate production incident ingestion and observe the normalization pipeline.</p>
            </div>

            {/* Sample Payloads */}
            <div className="flex gap-2 flex-wrap">
                {SAMPLE_INCIDENTS.map((s, i) => (
                    <button
                        key={i}
                        onClick={() => loadSample(i)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs bg-orange-50 text-orange-700 border border-orange-200 rounded hover:bg-orange-100 font-medium"
                    >
                        <FlaskConical className="w-3 h-3" />
                        {s.failure_type}
                    </button>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Editor */}
                <Card className="p-6 flex flex-col gap-4">
                    <h2 className="font-semibold flex items-center gap-2"><Upload className="w-4 h-4" /> Incident Payload</h2>
                    <textarea
                        value={jsonInput}
                        onChange={e => setJsonInput(e.target.value)}
                        className="font-mono text-xs bg-slate-950 text-green-400 rounded p-4 h-72 resize-none outline-none"
                        spellCheck={false}
                    />
                    <button
                        onClick={() => { void handleIngest(); }}
                        disabled={loading}
                        className="flex items-center justify-center gap-2 py-2.5 glass-dark-button rounded-lg font-medium disabled:opacity-50"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                        {loading ? 'Ingesting...' : 'INGEST INCIDENT'}
                    </button>
                    {error && <div className="text-red-600 text-sm bg-red-50 p-3 rounded border border-red-200">{error}</div>}
                </Card>

                {/* Pipeline Visualizer */}
                <Card className="p-6">
                    <h2 className="font-semibold mb-6">Ingestion Pipeline</h2>
                    <div className="space-y-2">
                        {PIPELINE_STEPS.map((step, i) => {
                            const isActive = ingestResult && (
                                step === 'RECEIVED' ||
                                (step === 'VALIDATED' && ['VALIDATED', 'NORMALIZED', 'PROCESSED'].includes(ingestResult.status)) ||
                                (step === 'NORMALIZED' && ['NORMALIZED', 'PROCESSED'].includes(ingestResult.status)) ||
                                (step === 'PROCESSED' && ingestResult.status === 'PROCESSED')
                            );
                            const isCurrent = ingestResult?.status === step;
                            return (
                                <div key={step} className="flex items-center gap-3">
                                    <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 transition-all ${isActive ? 'bg-green-500' : 'bg-slate-200'}`}>
                                        {isActive ? <CheckCircle2 className="w-4 h-4 text-white" /> : <span className="text-xs text-slate-500">{i + 1}</span>}
                                    </div>
                                    <div className={`flex-1 py-2 px-3 rounded ${isCurrent ? 'bg-green-50 border border-green-300' : isActive ? 'bg-slate-50' : 'bg-white'}`}>
                                        <div className={`font-semibold text-sm ${isActive ? 'text-green-800' : 'text-slate-500'}`}>{step}</div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {ingestResult && (
                        <div className="mt-6 p-4 bg-green-50 border border-green-300 rounded-lg">
                            <div className="font-bold text-green-800 flex items-center gap-2">
                                <CheckCircle2 className="w-5 h-5" />
                                INGESTION COMPLETE
                            </div>
                            <div className="mt-2 space-y-1 text-sm text-slate-700">
                                <div><span className="font-medium">External ID:</span> {ingestResult.external_incident_id}</div>
                                <div><span className="font-medium">Status:</span> {ingestResult.status}</div>
                                {ingestResult.normalized_incident_id && (
                                    <div><span className="font-medium">Normalized Incident:</span> <span className="font-mono text-xs">{ingestResult.normalized_incident_id}</span></div>
                                )}
                            </div>
                        </div>
                    )}
                </Card>
            </div>

            {/* History */}
            <Card className="overflow-hidden">
                <div className="px-6 py-4 border-b bg-white/40 backdrop-blur-md flex items-center justify-between">
                    <h2 className="font-semibold">Ingestion History</h2>
                    <button onClick={() => { void loadHistory(); }} className="text-xs text-blue-600 hover:underline">Refresh</button>
                </div>
                <div className="overflow-auto">
                    <table className="w-full text-sm">
                        <thead className="bg-white/40 backdrop-blur-md text-xs text-slate-500 uppercase tracking-wider">
                            <tr>
                                {['External ID', 'Source', 'Status', 'Normalized Incident', 'Received'].map(h => (
                                    <th key={h} className="px-4 py-3 text-left font-semibold">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {history.map(item => (
                                <tr key={item.id} className="hover:bg-white/40 backdrop-blur-md">
                                    <td className="px-4 py-3 font-mono text-xs font-semibold">{item.external_incident_id}</td>
                                    <td className="px-4 py-3">{item.source}</td>
                                    <td className="px-4 py-3">
                                        <span className={`text-xs font-bold px-2 py-0.5 rounded ${STATUS_COLORS[item.status] ?? 'bg-white/50 backdrop-blur-lg text-slate-700'}`}>
                                            {item.status}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3 font-mono text-xs">{item.normalized_incident_id ? item.normalized_incident_id.slice(0, 8) + '...' : '—'}</td>
                                    <td className="px-4 py-3 text-slate-500">{new Date(item.received_at).toLocaleString()}</td>
                                </tr>
                            ))}
                            {history.length === 0 && (
                                <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-400">No incidents ingested yet.</td></tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
