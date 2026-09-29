# Phase 4 — Incident Capture & Incident Intelligence Engine

## 1. Objective

Phase 4 converts meaningful Phase 3 failure experiment results into structured, queryable, reproducible **incidents**. Every incident is backed by real database state — no static mocks.

The full chain:

```
Phase 3 Failure Experiment
    ↓
Incident Detector (rules engine)
    ↓
Incident Capture (DB persistence)
    ↓
Evidence + Timeline + Root Cause
    ↓
Reproduction Specification
    ↓
Regression Candidate
    ↓
Phase 5 (Automated Test Generation)
```

---

## 2. Incident Lifecycle

```
OPEN → INVESTIGATING → REPRODUCED → RESOLVED → REGRESSION_CREATED → CLOSED
```

Status transitions are validated — arbitrary changes are rejected.

---

## 3. Detection Rules

| Rule | Trigger | Severity |
|------|---------|----------|
| **Rule 1** | `state_corrupted == True` | HIGH |
| **Rule 2** | `integrity_status == FAILED` | HIGH |
| **Rule 3** | Multiple confirmed submissions | CRITICAL |
| **Rule 4** | Invalid state regression | HIGH |
| **Rule 5** | Out-of-order event corruption | HIGH |

**Important**: A recovered failure (integrity SUCCESS) does NOT automatically create an incident. It is classified as `CONTROLLED FAILURE RECOVERED`.

---

## 4. Severity Rules

| Severity | Criteria |
|----------|----------|
| **CRITICAL** | Multiple confirmed submissions, data loss risk |
| **HIGH** | State corruption, invalid state regression |
| **MEDIUM** | Recoverable user-facing issue |
| **LOW** | Recovered failure, no persistent impact |

---

## 5. Category Classification

Derived deterministically from failure type and violation content:

| Category | Trigger |
|----------|---------|
| `DATA_INTEGRITY` | Multiple submission violations |
| `DUPLICATION` | DUPLICATE failure type |
| `EVENT_ORDERING` | OUT_OF_ORDER failure type |
| `TIMEOUT` | TIMEOUT or RETRY failure type |
| `STATE_MACHINE` | Invalid state regression |

---

## 6. Incident Fingerprinting

Every incident gets a deterministic MD5 fingerprint:

```
fingerprint = MD5(category:failure_type:target_event:first_violation)
```

Experiments with identical fingerprints map to the same `IncidentGroup`, tracking recurrence.

---

## 7. Database Schema

### New Tables (Migration 004)

| Table | Purpose |
|-------|---------|
| `incident_groups` | Groups identical failures by fingerprint |
| `incidents` | Core incident record |
| `incident_evidence` | Supporting evidence (snapshots, injections) |
| `incident_timeline` | Chronological event sequence |
| `incident_root_causes` | Deterministic root cause explanation |
| `incident_expectations` | Expected vs Actual state |
| `reproduction_specs` | How to re-trigger the failure |
| `regression_candidates` | Prepared for Phase 5 automation |

---

## 8. API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/v1/incidents` | List all incidents |
| `POST` | `/api/v1/incidents/detect` | Scan experiments and auto-detect |
| `GET` | `/api/v1/incidents/groups` | List incident groups |
| `GET` | `/api/v1/incidents/{id}` | Full incident detail |
| `POST` | `/api/v1/incidents/{id}/reproduce` | Execute reproduction |
| `POST` | `/api/v1/incidents/{id}/regression-candidate` | Create regression candidate |

---

## 9. Root Cause Rules

| Cause Code | Rule |
|-----------|------|
| `DUPLICATE_SIDE_EFFECT` | DUPLICATE failure + multiple submissions |
| `ORDERING_VIOLATION` | OUT_OF_ORDER failure + state corruption |

---

## 10. Reproduction Specification

Each incident stores a `ReproductionSpec` capturing:
- `initial_state` of the session
- `failure_configuration` (type, target, parameters)
- `expected_outcome` (CORRUPTED / RECOVERED)

This spec allows Phase 5 to deterministically regenerate the incident.

---

## 11. Testing

| Suite | Tests | Result |
|-------|-------|--------|
| Unit: IncidentDetector | 7 | ✅ PASS |
| Unit: IntegrityChecker | 7 | ✅ PASS |
| Unit: FailureInjector | 14 | ✅ PASS |
| Unit: StateMachine | 12 | ✅ PASS |
| Integration: ExamWorkflow | 6 | ✅ PASS |
| **TOTAL** | **70** | **✅ 70 passed, 3 skipped** |

---

## 12. Phase 5 Integration

The `regression_candidates` table is the interface to Phase 5.

Each record contains:
- `reproduction_spec_id` → exact failure parameters
- `trigger_condition` → test setup description
- `expected_behavior` → assertion to encode
- `invariant` → the system property that must hold
- `status` → PENDING until Phase 5 generates code
