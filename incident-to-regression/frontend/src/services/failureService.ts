import { apiClient } from './api';
import type { 
    FailureScenario, 
    FailureExperiment, 
    ExperimentDetails, 
    InjectedEvent,
    ReliabilityMetrics
} from '../types/failure';

export const failureService = {
    async createScenario(scenario: Partial<FailureScenario>): Promise<{ data: { id: string, status: string } }> {
        const response = await apiClient.post<{ data: { id: string, status: string } }>('/api/v1/failure/scenarios', scenario);
        return response.data;
    },

    async listScenarios(): Promise<{ items: FailureScenario[] }> {
        const response = await apiClient.get<{ items: FailureScenario[] }>('/api/v1/failure/scenarios');
        return response.data;
    },

    async runScenario(scenarioId: string, sessionId: string): Promise<{ data: { experiment_id: string, status: string } }> {
        const response = await apiClient.post<{ data: { experiment_id: string, status: string } }>(`/api/v1/failure/scenarios/${scenarioId}/run`, { session_id: sessionId });
        return response.data;
    },

    async listExperiments(): Promise<{ items: FailureExperiment[] }> {
        const response = await apiClient.get<{ items: FailureExperiment[] }>('/api/v1/failure/experiments');
        return response.data;
    },

    async getExperiment(experimentId: string): Promise<ExperimentDetails> {
        const response = await apiClient.get<ExperimentDetails>(`/api/v1/failure/experiments/${experimentId}`);
        return response.data;
    },

    async getExperimentTrace(experimentId: string): Promise<{ items: InjectedEvent[] }> {
        const response = await apiClient.get<{ items: InjectedEvent[] }>(`/api/v1/failure/experiments/${experimentId}/trace`);
        return response.data;
    },

    async getMetrics(): Promise<ReliabilityMetrics> {
        const response = await apiClient.get<ReliabilityMetrics>('/api/v1/failure/metrics');
        return response.data;
    }
};
