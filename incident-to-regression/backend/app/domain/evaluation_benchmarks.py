from typing import List, Dict, Any

BENCHMARKS: List[Dict[str, Any]] = [
    {
        "benchmark_id": "BENCH-001",
        "scenario_name": "Duplicate submission",
        "description": "A student attempts to submit an exam twice due to UI glitch or network retry.",
        "failure_type": "DUPLICATE",
        "category": "DUPLICATION",
        "severity": "HIGH",
        "tags": ["submission", "retry", "network"],
        "scenario_config": {
            "type": "DUPLICATE",
            "event_type": "SUBMIT_REQUESTED",
            "count": 2,
            "delay_ms": 100
        }
    },
    {
        "benchmark_id": "BENCH-002",
        "scenario_name": "Delayed answer event",
        "description": "An answer event is delayed and arrives after the submission event.",
        "failure_type": "DELAY",
        "category": "TIMING",
        "severity": "MEDIUM",
        "tags": ["answer", "network", "timing"],
        "scenario_config": {
            "type": "DELAY",
            "event_type": "ANSWER_SELECTED",
            "delay_ms": 5000
        }
    },
    {
        "benchmark_id": "BENCH-003",
        "scenario_name": "Out-of-order answer event",
        "description": "An answer for question 2 arrives before the view event for question 2.",
        "failure_type": "OUT_OF_ORDER",
        "category": "ORDERING",
        "severity": "LOW",
        "tags": ["answer", "ordering"],
        "scenario_config": {
            "type": "OUT_OF_ORDER",
            "event_type": "ANSWER_SELECTED",
            "swap_with": "QUESTION_VIEWED"
        }
    },
    {
        "benchmark_id": "BENCH-004",
        "scenario_name": "Timeout followed by retry",
        "description": "A timeout causes a client to drop connection and retry submission, causing state confusion.",
        "failure_type": "TIMEOUT",
        "category": "NETWORK",
        "severity": "HIGH",
        "tags": ["network", "timeout", "submission"],
        "scenario_config": {
            "type": "TIMEOUT",
            "event_type": "SUBMIT_REQUESTED",
            "duration_ms": 15000
        }
    },
    {
        "benchmark_id": "BENCH-005",
        "scenario_name": "Network interruption",
        "description": "Network drops completely during the session sync, losing a batch of events.",
        "failure_type": "DROP",
        "category": "NETWORK",
        "severity": "CRITICAL",
        "tags": ["network", "drop", "session"],
        "scenario_config": {
            "type": "DROP",
            "event_type": "HEARTBEAT",
            "count": 3
        }
    },
    {
        "benchmark_id": "BENCH-006",
        "scenario_name": "Duplicate answer save",
        "description": "The exact same answer is saved twice, potentially violating primary key constraints or history logs.",
        "failure_type": "DUPLICATE",
        "category": "DUPLICATION",
        "severity": "LOW",
        "tags": ["answer", "duplicate"],
        "scenario_config": {
            "type": "DUPLICATE",
            "event_type": "ANSWER_SAVED",
            "count": 2,
            "delay_ms": 10
        }
    },
    {
        "benchmark_id": "BENCH-007",
        "scenario_name": "Invalid state transition",
        "description": "A start exam event is received when the exam is already completed.",
        "failure_type": "CORRUPTION",
        "category": "STATE",
        "severity": "HIGH",
        "tags": ["state", "session"],
        "scenario_config": {
            "type": "MUTATE",
            "event_type": "EXAM_STARTED",
            "mutation_target": "session_status",
            "mutation_value": "COMPLETED"
        }
    },
    {
        "benchmark_id": "BENCH-008",
        "scenario_name": "Session lifecycle failure",
        "description": "End event arrives without a start event being registered.",
        "failure_type": "DROP",
        "category": "LIFECYCLE",
        "severity": "MEDIUM",
        "tags": ["session", "lifecycle"],
        "scenario_config": {
            "type": "DROP",
            "event_type": "EXAM_STARTED",
            "count": 1
        }
    },
    {
        "benchmark_id": "BENCH-009",
        "scenario_name": "Submission finalization failure",
        "description": "Database lock timeout during submission finalization.",
        "failure_type": "INFRASTRUCTURE",
        "category": "DATABASE",
        "severity": "CRITICAL",
        "tags": ["database", "submission"],
        "scenario_config": {
            "type": "ERROR",
            "event_type": "SUBMISSION_FINALIZED",
            "error_type": "DB_LOCK_TIMEOUT"
        }
    },
    {
        "benchmark_id": "BENCH-010",
        "scenario_name": "Event processing failure",
        "description": "Malformed JSON payload causes the event processor to crash.",
        "failure_type": "MALFORMED",
        "category": "PROCESSING",
        "severity": "MEDIUM",
        "tags": ["parsing", "event"],
        "scenario_config": {
            "type": "MUTATE",
            "event_type": "ANY",
            "mutation_target": "payload",
            "mutation_value": "INVALID_JSON_{"
        }
    }
]
