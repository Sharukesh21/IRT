export type FailureType = 
    | "NONE"
    | "DELAY"
    | "DUPLICATE"
    | "OUT_OF_ORDER"
    | "NETWORK_INTERRUPTION"
    | "TIMEOUT"
    | "RETRY";

export type RecoveryStatus = "SUCCESS" | "FAILED" | "UNKNOWN";

export interface FailureScenario {
    id: string;
    name: string;
    description?: string;
    failure_type: FailureType;
    target_event_type?: string;
    target_event_id?: string;
    parameters: Record<string, unknown>;
    seed?: number;
    enabled: boolean;
    created_at: string;
}

export interface FailureExperiment {
    id: string;
    scenario_id: string;
    session_id: string;
    started_at: string;
    completed_at?: string;
    initial_state: string;
    final_state?: string;
    event_count: number;
    duplicate_count: number;
    delayed_count: number;
    out_of_order_count: number;
    error_count: number;
    recovery_status: RecoveryStatus;
    state_corrupted: boolean;
    processing_time_ms?: number;
}

export interface IntegrityResult {
    id: string;
    experiment_id: string;
    status: string;
    state_corrupted: boolean;
    expected_state: string;
    actual_state: string;
    submission_count: number;
    violations: string[];
}

export interface InjectedEvent {
    id: string;
    experiment_id: string;
    original_event_id?: string;
    injected_event_id: string;
    failure_type: FailureType;
    modification: string;
    original_sequence?: number;
    delivery_sequence: number;
    occurred_at: string;
    received_at: string;
    status: string;
}

export interface ExperimentDetails {
    experiment: FailureExperiment;
    integrity: IntegrityResult;
    scenario: FailureScenario;
}

export interface ReliabilityMetrics {
    total_experiments: number;
    recovery_rate: number;
    corruption_rate: number;
}
