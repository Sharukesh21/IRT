import { apiClient } from './api';
import type { RegressionTest, RegressionTestRun, RegressionCandidate, RegressionProof, RegressionAssertionResult } from '../types/regression';

export const regressionService = {
    async listCandidates(): Promise<{ items: RegressionCandidate[] }> {
        const response = await apiClient.get<{ items: RegressionCandidate[] }>('/api/v1/regression/candidates');
        return response.data;
    },
    async generateTest(candidateId: string): Promise<{ status: string; test_id: string }> {
        const response = await apiClient.post<{ status: string; test_id: string }>(`/api/v1/regression/candidates/${candidateId}/generate`, {});
        return response.data;
    },
    async listTests(): Promise<{ items: RegressionTest[] }> {
        const response = await apiClient.get<{ items: RegressionTest[] }>('/api/v1/regression/tests');
        return response.data;
    },
    async getTest(testId: string): Promise<{ test: RegressionTest; proof: RegressionProof; runs: RegressionTestRun[] }> {
        const response = await apiClient.get<{ test: RegressionTest; proof: RegressionProof; runs: RegressionTestRun[] }>(`/api/v1/regression/tests/${testId}`);
        return response.data;
    },
    async runTest(testId: string): Promise<{ job_id: string; status: string }> {
        const response = await apiClient.post<{ job_id: string; status: string }>(`/api/v1/regression/tests/${testId}/run`, {});
        return response.data;
    },
    async getRun(runId: string): Promise<{ run: RegressionTestRun; assertions: RegressionAssertionResult[] }> {
        const response = await apiClient.get<{ run: RegressionTestRun; assertions: RegressionAssertionResult[] }>(`/api/v1/regression/runs/${runId}`);
        return response.data;
    },
    async runSuite(): Promise<{ job_id: string; status: string }> {
        const response = await apiClient.post<{ job_id: string; status: string }>('/api/v1/regression/suite/run', {});
        return response.data;
    },
    async getMetrics(): Promise<{ total_tests: number; total_runs: number; pass_rate: number }> {
        const response = await apiClient.get<{ total_tests: number; total_runs: number; pass_rate: number }>('/api/v1/regression/metrics');
        return response.data;
    }
};
