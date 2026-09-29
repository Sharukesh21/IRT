import { useState, useEffect } from 'react';
import { failureService } from '../services/failureService';
import type { FailureScenario, FailureType, ExperimentDetails } from '../types/failure';
import { Card } from '../components/ui/Card';
import { AlertCircle, CheckCircle2, ServerCrash, Clock, AlertTriangle } from 'lucide-react';

type NewScenario = {
    name: string;
    failure_type: FailureType;
    target_event_type: string;
    delay_ms: number;
    count: number;
};

export function SimulatorPage() {
    const [scenarios, setScenarios] = useState<FailureScenario[]>([]);
    const [selectedScenario, setSelectedScenario] = useState<string>('');
    const [selectedSession, setSelectedSession] = useState<string>('');

    const [newScenario, setNewScenario] = useState<NewScenario>({
        name: 'Duplicate Submit',
        failure_type: 'DUPLICATE',
        target_event_type: 'SUBMIT_REQUESTED',
        delay_ms: 1000,
        count: 2
    });

    const [running, setRunning] = useState(false);
    const [result, setResult] = useState<ExperimentDetails | null>(null);

    useEffect(() => {
        const loadScenarios = async () => {
            try {
                const res = await failureService.listScenarios();
                setScenarios(res.items);
            } catch (err) {
                console.error("Failed to load scenarios", err);
            }
        };
        void loadScenarios();
    }, []);

    const handleCreateScenario = async () => {
        const params: Record<string, number> = {};
        if (newScenario.failure_type === 'DELAY') params.delay_ms = newScenario.delay_ms;
        if (newScenario.failure_type === 'DUPLICATE') params.count = newScenario.count;
        if (newScenario.failure_type === 'TIMEOUT') params.timeout_ms = newScenario.delay_ms;

        const res = await failureService.createScenario({
            name: newScenario.name,
            failure_type: newScenario.failure_type,
            target_event_type: newScenario.target_event_type,
            parameters: params
        });

        const scenRes = await failureService.listScenarios();
        setScenarios(scenRes.items);
        setSelectedScenario(res.data.id);
    };

    const handleRunScenario = async () => {
        if (!selectedScenario || !selectedSession) return;
        setRunning(true);
        setResult(null);
        try {
            const res = await failureService.runScenario(selectedScenario, selectedSession);
            const details = await failureService.getExperiment(res.data.experiment_id);
            setResult(details);
        } catch (e) {
            console.error(e);
            alert("Failed to run experiment");
        } finally {
            setRunning(false);
        }
    };

    const isRecovered = result?.experiment.recovery_status === 'SUCCESS';

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-6">
            <h1 className="text-3xl font-bold tracking-tight mb-2">Failure Simulation Laboratory</h1>
            <p className="text-slate-500 mb-8">Inject controlled, deterministic failures and observe system recovery.</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Configuration Panel */}
                <Card className="p-6 space-y-4">
                    <h2 className="text-xl font-semibold border-b pb-2">1. Scenario Configuration</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-1">Failure Type</label>
                            <select
                                className="w-full p-2 border rounded-md glass"
                                value={newScenario.failure_type}
                                onChange={(e) => setNewScenario({ ...newScenario, failure_type: e.target.value as FailureType })}
                            >
                                <option value="DUPLICATE">DUPLICATE</option>
                                <option value="DELAY">DELAY</option>
                                <option value="OUT_OF_ORDER">OUT_OF_ORDER</option>
                                <option value="TIMEOUT">TIMEOUT</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-1">Target Event</label>
                            <select
                                className="w-full p-2 border rounded-md glass"
                                value={newScenario.target_event_type}
                                onChange={(e) => setNewScenario({ ...newScenario, target_event_type: e.target.value })}
                            >
                                <option value="SUBMIT_REQUESTED">SUBMIT_REQUESTED</option>
                                <option value="ANSWER_SAVED">ANSWER_SAVED</option>
                            </select>
                        </div>

                        {newScenario.failure_type === 'DUPLICATE' && (
                            <div>
                                <label className="block text-sm font-medium mb-1">Duplicate Count</label>
                                <input
                                    type="number"
                                    className="w-full p-2 border rounded-md"
                                    value={newScenario.count}
                                    onChange={e => setNewScenario({ ...newScenario, count: parseInt(e.target.value) })}
                                />
                            </div>
                        )}

                        {(newScenario.failure_type === 'DELAY' || newScenario.failure_type === 'TIMEOUT') && (
                            <div>
                                <label className="block text-sm font-medium mb-1">Delay / Timeout (ms)</label>
                                <input
                                    type="number"
                                    className="w-full p-2 border rounded-md"
                                    value={newScenario.delay_ms}
                                    onChange={e => setNewScenario({ ...newScenario, delay_ms: parseInt(e.target.value) })}
                                />
                            </div>
                        )}

                        <button
                            onClick={() => { void handleCreateScenario(); }}
                            className="bg-slate-800 text-white px-4 py-2 rounded-md hover:bg-slate-700 transition"
                        >
                            Create Scenario
                        </button>
                    </div>

                    {scenarios.length > 0 && (
                        <div>
                            <label className="block text-sm font-medium mb-1">Select Saved Scenario</label>
                            <select
                                className="w-full p-2 border rounded-md glass"
                                value={selectedScenario}
                                onChange={e => setSelectedScenario(e.target.value)}
                            >
                                <option value="">-- Select --</option>
                                {scenarios.map(s => (
                                    <option key={s.id} value={s.id}>{s.name} ({s.failure_type})</option>
                                ))}
                            </select>
                        </div>
                    )}

                    <div className="mt-4">
                        <label className="block text-sm font-medium mb-1">Session ID (from Phase 2)</label>
                        <input
                            type="text"
                            className="w-full p-2 border rounded-md font-mono text-sm"
                            placeholder="e.g. 550e8400-e29b-41d4-a716-446655440000"
                            value={selectedSession}
                            onChange={(e) => setSelectedSession(e.target.value)}
                        />
                        <p className="text-xs text-slate-500 mt-1">Provide an existing session ID that has events.</p>
                    </div>

                    <div className="pt-4 mt-4 border-t">
                        <button
                            disabled={!selectedScenario || !selectedSession || running}
                            onClick={() => { void handleRunScenario(); }}
                            className={`w-full py-3 rounded-md font-bold transition flex justify-center items-center gap-2 ${
                                !selectedScenario || !selectedSession || running
                                    ? 'bg-slate-200 text-slate-400 cursor-not-allowed'
                                    : 'bg-red-600 text-white hover:bg-red-700 shadow-lg'
                            }`}
                        >
                            {running ? <>Running Experiment...</> : <><ServerCrash className="w-5 h-5" /> Run Scenario</>}
                        </button>
                    </div>
                </Card>

                {/* Results Panel */}
                <Card className="p-6 bg-white/40 backdrop-blur-md min-h-[500px]">
                    <h2 className="text-xl font-semibold border-b pb-2 mb-4">2. Execution Result</h2>

                    {!result && !running && (
                        <div className="h-full flex flex-col items-center justify-center text-slate-400">
                            <ServerCrash className="w-16 h-16 mb-4 opacity-20" />
                            <p>Configure and run a scenario to see results.</p>
                        </div>
                    )}

                    {running && (
                        <div className="h-full flex flex-col items-center justify-center text-blue-500 animate-pulse">
                            <Clock className="w-12 h-12 mb-4" />
                            <p className="font-medium">Applying failure injection...</p>
                        </div>
                    )}

                    {result && !running && (
                        <div className="space-y-6">
                            <div className={`p-4 rounded-lg flex items-center gap-3 border ${
                                isRecovered
                                    ? 'bg-green-50 border-green-200 text-green-800'
                                    : 'bg-red-50 border-red-200 text-red-800'
                            }`}>
                                {isRecovered
                                    ? <CheckCircle2 className="w-8 h-8 flex-shrink-0" />
                                    : <AlertTriangle className="w-8 h-8 flex-shrink-0" />}
                                <div>
                                    <h3 className="text-lg font-bold">
                                        {isRecovered ? 'RECOVERED ✓' : 'STATE CORRUPTED ✕'}
                                    </h3>
                                    <p className="text-sm opacity-80">
                                        {isRecovered
                                            ? 'The system successfully defended against the injected failure.'
                                            : 'The injected failure bypassed systemic invariants.'}
                                    </p>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="p-3 glass border rounded-md">
                                    <div className="text-xs text-slate-500 uppercase">Failure Type</div>
                                    <div className="font-mono font-medium">{result.scenario.failure_type}</div>
                                </div>
                                <div className="p-3 glass border rounded-md">
                                    <div className="text-xs text-slate-500 uppercase">Final State</div>
                                    <div className="font-mono font-medium">{result.experiment.final_state ?? 'UNKNOWN'}</div>
                                </div>
                                <div className="p-3 glass border rounded-md">
                                    <div className="text-xs text-slate-500 uppercase">Submission Count</div>
                                    <div className="font-mono font-medium">{result.integrity.submission_count}</div>
                                </div>
                                <div className="p-3 glass border rounded-md">
                                    <div className="text-xs text-slate-500 uppercase">Processing Time</div>
                                    <div className="font-mono font-medium">
                                        {result.experiment.processing_time_ms != null
                                            ? `${result.experiment.processing_time_ms.toFixed(1)} ms`
                                            : '-'}
                                    </div>
                                </div>
                            </div>

                            {result.integrity.violations.length > 0 && (
                                <div className="p-4 bg-red-50 border border-red-100 rounded-md">
                                    <h4 className="font-bold text-red-800 flex items-center gap-2 mb-2">
                                        <AlertCircle className="w-4 h-4" /> Invariant Violations
                                    </h4>
                                    <ul className="list-disc pl-5 text-sm text-red-700 space-y-1">
                                        {result.integrity.violations.map((v, i) => (
                                            <li key={i}>{v}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    )}
                </Card>
            </div>
        </div>
    );
}
