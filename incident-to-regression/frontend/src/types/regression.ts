export interface RegressionCandidate {
    id: string;
    candidate_id: string;
    incident_id: string;
    name: string;
    description: string;
    trigger_condition: string;
    expected_behavior: string;
    invariant: string;
    priority: string;
    status: string;
    created_at: string;
}

export interface RegressionTest {
    id: string;
    test_id: string;
    candidate_id: string;
    incident_id: string;
    name: string;
    description: string;
    category: string;
    failure_type: string;
    priority: string;
    status: string;
    version: number;
    test_definition: Record<string, unknown>;
    created_at: string;
}

export interface RegressionTestRun {
    id: string;
    run_id: string;
    test_id: string;
    started_at: string;
    duration_ms: number;
    status: string;
    assertions_total: number;
    assertions_passed: number;
    assertions_failed: number;
    execution_trace: Record<string, unknown>[];
    created_at: string;
}

export interface RegressionAssertionResult {
    path: string;
    operator: string;
    expected_value: string;
    actual_value: string;
    status: string;
    message?: string;
}

export interface RegressionProof {
    before_status: string;
    after_status: string;
    protected: boolean;
}
