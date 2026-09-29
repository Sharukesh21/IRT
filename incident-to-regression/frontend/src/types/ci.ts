export interface ExternalIncident {
    id: string;
    external_incident_id: string;
    source: string;
    raw_payload: Record<string, unknown>;
    normalized_incident_id?: string;
    status: string;
    error?: string;
    received_at: string;
    processed_at?: string;
}

export interface RegressionOrchestration {
    id: string;
    orchestration_id: string;
    incident_id?: string;
    plan_id?: string;
    trigger_source: string;
    status: string;
    started_at?: string;
    completed_at?: string;
    total_tests: number;
    passed: number;
    failed: number;
    errors: number;
    created_at: string;
}

export interface CIRegressionRun {
    id: string;
    run_id: string;
    orchestration_id?: string;
    provider?: string;
    repository?: string;
    branch?: string;
    commit_sha?: string;
    pull_request_number?: number;
    status: string;
    started_at: string;
    completed_at?: string;
    created_at: string;
}

export interface RegressionPolicy {
    id: string;
    policy_name: string;
    strategy: string;
    block_on_failure: boolean;
    required_severity?: string;
    enabled: boolean;
    created_at: string;
}

export interface RegressionEscape {
    id: string;
    incident_id: string;
    test_id: string;
    detected_at: string;
    test_last_status: string;
    explanation?: string;
}

export interface CIMetrics {
    incidents_total: number;
    tests_total: number;
    escapes_total: number;
    external_ingested: number;
    ci_pass_rate: number;
}

export const SAMPLE_INCIDENTS = [
    {
        external_incident_id: "PROD-DEMO-001",
        title: "Duplicate submission detected",
        description: "A student submission was processed twice due to network retry.",
        severity: "HIGH",
        failure_type: "DUPLICATE",
        event_type: "SUBMIT_REQUESTED",
        category: "DUPLICATION",
        service: "exam-submission",
        environment: "production",
        source: "SIMULATED_PRODUCTION"
    },
    {
        external_incident_id: "PROD-DEMO-002",
        title: "Out-of-order answer event",
        description: "Answer was received before question view event.",
        severity: "MEDIUM",
        failure_type: "OUT_OF_ORDER",
        event_type: "ANSWER_SELECTED",
        category: "ORDERING",
        service: "exam-session",
        environment: "production",
        source: "SIMULATED_PRODUCTION"
    },
    {
        external_incident_id: "PROD-DEMO-003",
        title: "Timeout retry causing duplicate",
        description: "Network timeout caused client to retry submission.",
        severity: "HIGH",
        failure_type: "TIMEOUT",
        event_type: "SUBMIT_REQUESTED",
        category: "NETWORK",
        service: "exam-submission",
        environment: "production",
        source: "SIMULATED_PRODUCTION"
    },
    {
        external_incident_id: "PROD-DEMO-004",
        title: "Delayed answer event",
        description: "Student answer arrived after exam session closed.",
        severity: "LOW",
        failure_type: "DELAY",
        event_type: "ANSWER_SAVED",
        category: "TIMING",
        service: "exam-session",
        environment: "staging",
        source: "SIMULATED_PRODUCTION"
    },
    {
        external_incident_id: "PROD-DEMO-005",
        title: "Network interruption during submission",
        description: "Student lost network connection while submitting exam.",
        severity: "MEDIUM",
        failure_type: "DUPLICATE",
        event_type: "SUBMIT_REQUESTED",
        category: "NETWORK",
        service: "exam-submission",
        environment: "production",
        source: "SIMULATED_PRODUCTION"
    }
];
