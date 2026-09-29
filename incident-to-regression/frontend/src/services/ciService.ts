import { apiClient } from './api';
import type { ExternalIncident, RegressionOrchestration, CIRegressionRun, RegressionPolicy, RegressionEscape, CIMetrics } from '../types/ci';

export const ciService = {
    async ingestIncident(payload: Record<string, unknown>): Promise<{ status: string; external_incident_id: string; normalized_incident_id?: string }> {
        const res = await apiClient.post<{ status: string; external_incident_id: string; normalized_incident_id?: string }>('/api/v1/ci/incidents/ingest', payload);
        return res.data;
    },
    async listExternalIncidents(): Promise<{ items: ExternalIncident[] }> {
        const res = await apiClient.get<{ items: ExternalIncident[] }>('/api/v1/ci/incidents');
        return res.data;
    },
    async triggerCIRun(payload: { incident_id: string; strategy: string; commit_sha?: string; branch?: string; pull_request_number?: number }): Promise<{ status: string; tests: number; passed: number; failed: number; errors: number; orchestration_id: string; ci_run_id: string }> {
        const res = await apiClient.post<{ status: string; tests: number; passed: number; failed: number; errors: number; orchestration_id: string; ci_run_id: string }>('/api/v1/ci/regression/run', payload);
        return res.data;
    },
    async listOrchestrations(): Promise<{ items: RegressionOrchestration[] }> {
        const res = await apiClient.get<{ items: RegressionOrchestration[] }>('/api/v1/ci/orchestrations');
        return res.data;
    },
    async listCIRuns(): Promise<{ items: CIRegressionRun[] }> {
        const res = await apiClient.get<{ items: CIRegressionRun[] }>('/api/v1/ci/runs');
        return res.data;
    },
    async listPolicies(): Promise<{ items: RegressionPolicy[] }> {
        const res = await apiClient.get<{ items: RegressionPolicy[] }>('/api/v1/ci/policies');
        return res.data;
    },
    async createPolicy(policy: { policy_name: string; strategy: string; block_on_failure: boolean; required_severity?: string }): Promise<void> {
        await apiClient.post('/api/v1/ci/policies', policy);
    },
    async listEscapes(): Promise<{ items: RegressionEscape[] }> {
        const res = await apiClient.get<{ items: RegressionEscape[] }>('/api/v1/ci/escapes');
        return res.data;
    },
    async getMetrics(): Promise<CIMetrics> {
        const res = await apiClient.get<CIMetrics>('/api/v1/ci/metrics');
        return res.data;
    }
};
