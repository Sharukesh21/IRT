export interface Incident {
    id: string;
    incident_id: string;
    title: string;
    description: string;
    status: string;
    severity: string;
    category: string;
    failure_type: string;
    session_id: string;
    experiment_id: string;
    primary_event_id: string;
    occurred_at: string;
    reproducible: boolean;
    regression_candidate: boolean;
    state_corrupted: boolean;
    recovery_status: string;
}

export interface IncidentGroup {
    id: string;
    group_key: string;
    category: string;
    failure_type: string;
    occurrence_count: number;
    last_seen_at: string;
    status: string;
}

export interface IncidentTimeline {
    id: string;
    sequence: number;
    event_type: string;
    occurred_at: string;
    received_at: string;
    processing_status: string;
    failure_type: string;
    is_anomalous: boolean;
}

export interface IncidentExpectation {
    expected_state: Record<string, unknown>;
    actual_state: Record<string, unknown>;
    invariant_violations: string[];
}

export interface IncidentRootCause {
    cause_code: string;
    explanation: string;
    confidence: string;
}

export interface ReproductionSpec {
    reproduction_id: string;
    initial_state: string;
    expected_outcome: string;
    failure_configuration: Record<string, unknown>;
}

export interface RegressionCandidate {
    candidate_id: string;
    name: string;
    trigger_condition: string;
    status: string;
}

export interface IncidentDetails {
    incident: Incident;
    timeline: IncidentTimeline[];
    expectations: IncidentExpectation;
    root_cause: IncidentRootCause;
    reproduction: ReproductionSpec;
    regression_candidate?: RegressionCandidate;
}
