import { useState, useEffect } from 'react';
import { failureService } from '../services/failureService';
import type { FailureExperiment, ReliabilityMetrics } from '../types/failure';
import { Card } from '../components/ui/Card';
import { Activity, ShieldAlert, ShieldCheck } from 'lucide-react';

export function MetricsPage() {
    const [metrics, setMetrics] = useState<ReliabilityMetrics | null>(null);
    const [experiments, setExperiments] = useState<FailureExperiment[]>([]);

    useEffect(() => {
        const load = async () => {
            try {
                const metRes = await failureService.getMetrics();
                setMetrics(metRes);
                const expRes = await failureService.listExperiments();
                setExperiments(expRes.items);
            } catch (err) {
                console.error(err);
            }
        };
        void load();
    }, []);

    return (
        <div className="p-6 max-w-6xl mx-auto space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight mb-2">Reliability Metrics</h1>
                <p className="text-slate-500">Phase 3 System Resilience &amp; Recovery Statistics</p>
            </div>

            {metrics && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Card className="p-6 glass border flex items-center gap-4">
                        <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
                            <Activity className="w-8 h-8" />
                        </div>
                        <div>
                            <div className="text-sm font-medium text-slate-500">Total Experiments</div>
                            <div className="text-3xl font-bold">{metrics.total_experiments}</div>
                        </div>
                    </Card>
                    <Card className="p-6 glass border flex items-center gap-4">
                        <div className="p-3 bg-green-50 text-green-600 rounded-lg">
                            <ShieldCheck className="w-8 h-8" />
                        </div>
                        <div>
                            <div className="text-sm font-medium text-slate-500">Recovery Rate</div>
                            <div className="text-3xl font-bold">{metrics.recovery_rate}%</div>
                        </div>
                    </Card>
                    <Card className="p-6 glass border flex items-center gap-4">
                        <div className="p-3 bg-red-50 text-red-600 rounded-lg">
                            <ShieldAlert className="w-8 h-8" />
                        </div>
                        <div>
                            <div className="text-sm font-medium text-slate-500">State Corruption Rate</div>
                            <div className="text-3xl font-bold">{metrics.corruption_rate}%</div>
                        </div>
                    </Card>
                </div>
            )}

            {!metrics && (
                <div className="text-slate-400 text-center py-8">
                    No experiments yet. Go to Simulator to run one.
                </div>
            )}

            <Card className="p-6 overflow-hidden">
                <h2 className="text-xl font-semibold mb-4">Experiment History</h2>
                <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                        <thead className="bg-white/40 backdrop-blur-md text-slate-600 border-b">
                            <tr>
                                <th className="px-4 py-3 font-medium">ID</th>
                                <th className="px-4 py-3 font-medium">Session</th>
                                <th className="px-4 py-3 font-medium">Date</th>
                                <th className="px-4 py-3 font-medium">Final State</th>
                                <th className="px-4 py-3 font-medium">Recovery</th>
                                <th className="px-4 py-3 font-medium">Duration</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y">
                            {experiments.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-4 py-8 text-center text-slate-500">
                                        No experiments yet.
                                    </td>
                                </tr>
                            ) : (
                                experiments.map(exp => (
                                    <tr key={exp.id} className="hover:bg-white/40 backdrop-blur-md">
                                        <td className="px-4 py-3 font-mono text-xs">{exp.id.slice(0, 8)}...</td>
                                        <td className="px-4 py-3 font-mono text-xs">{exp.session_id.slice(0, 8)}...</td>
                                        <td className="px-4 py-3 whitespace-nowrap text-xs">
                                            {new Date(exp.started_at).toLocaleString()}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="bg-white/50 backdrop-blur-lg px-2 py-1 rounded text-xs font-medium">
                                                {exp.final_state ?? 'UNKNOWN'}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3">
                                            {exp.recovery_status === 'SUCCESS' ? (
                                                <span className="text-green-600 font-medium flex items-center gap-1 text-xs">
                                                    <ShieldCheck className="w-3 h-3" /> SUCCESS
                                                </span>
                                            ) : (
                                                <span className="text-red-600 font-medium flex items-center gap-1 text-xs">
                                                    <ShieldAlert className="w-3 h-3" /> FAILED
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-4 py-3 font-mono text-xs">
                                            {exp.processing_time_ms != null ? `${exp.processing_time_ms.toFixed(1)}ms` : '-'}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </Card>
        </div>
    );
}
