import { apiClient } from './api';
import type { Incident, IncidentGroup, IncidentDetails } from '../types/incident';

export const incidentService = {
    async listIncidents(): Promise<{ items: Incident[] }> {
        const response = await apiClient.get<{ items: Incident[] }>('/api/v1/incidents');
        return response.data;
    },
    async detectIncidents(): Promise<{ job_id: string; status: string }> {
        const response = await apiClient.post<{ job_id: string; status: string; message: string }>('/api/v1/incidents/detect', {});
        return response.data;
    },
    async listGroups(): Promise<{ items: IncidentGroup[] }> {
        const response = await apiClient.get<{ items: IncidentGroup[] }>('/api/v1/incidents/groups');
        return response.data;
    },
    async getIncident(incidentId: string): Promise<IncidentDetails> {
        const response = await apiClient.get<IncidentDetails>(`/api/v1/incidents/${incidentId}`);
        return response.data;
    },
    async reproduce(incidentId: string): Promise<{ status: string; original_outcome: string; reproduced_outcome: string; match: boolean }> {
        const response = await apiClient.post<{ status: string; original_outcome: string; reproduced_outcome: string; match: boolean }>(`/api/v1/incidents/${incidentId}/reproduce`, {});
        return response.data;
    },
    async createRegressionCandidate(incidentId: string): Promise<{ candidate_id: string }> {
        const response = await apiClient.post<{ status: string; candidate_id: string }>(`/api/v1/incidents/${incidentId}/regression-candidate`, {});
        return response.data;
    }
};

