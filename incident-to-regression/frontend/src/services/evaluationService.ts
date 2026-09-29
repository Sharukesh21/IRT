import { apiClient } from './api';
import type { EvaluationBenchmark, EvaluationMetrics } from '../types/evaluation';

export const evaluationService = {
    async seedBenchmarks(): Promise<{ status: string }> {
        const res = await apiClient.post<{ status: string }>('/api/v1/evaluation/seed');
        return res.data;
    },
    async listBenchmarks(): Promise<{ items: EvaluationBenchmark[] }> {
        const res = await apiClient.get<{ items: EvaluationBenchmark[] }>('/api/v1/evaluation/benchmarks');
        return res.data;
    },
    async runExperiment(benchmarkId: string): Promise<{ status: string; experiment_id: string }> {
        const res = await apiClient.post<{ status: string; experiment_id: string }>(`/api/v1/evaluation/experiments/run?benchmark_id=${benchmarkId}`);
        return res.data;
    },
    async getMetrics(): Promise<EvaluationMetrics> {
        const res = await apiClient.get<EvaluationMetrics>('/api/v1/evaluation/metrics');
        return res.data;
    }
};
