# Phase 5 — Incident-to-Regression Automation

## 1. Objective

Phase 5 solves the capstone's core requirement: automatically converting verified incidents (Phase 4) into executable regression tests (Phase 5) that prove the original issue is protected against recurrence.

The full flow:
`Incident -> Reproduction -> Regression Candidate -> Structured Test DSL -> Execution -> Assertion Result -> Regression Proof`

---

## 2. Architecture

We integrated test generation directly into the domain logic by extending Phase 2's Event Processor and Phase 3's Failure Injector.

```
Candidate -> Test Generator -> RegressionTest (DSL) -> Test Runner -> EventProcessor -> Assertions -> TestRun
```

### Components Built

- **Test Generator:** Analyzes `Incident` and `ReproductionSpec` to construct an isolated, structured `RegressionTest` definition.
- **Assertion Engine:** Processes final system state using standard logic operators (EQUALS, CONTAINS, EXISTS, etc.)
- **Test Runner:** Creates an isolated state (fresh ExamSession), maps the abstract events to real `DomainEvent` instances, applies `FailureConfiguration` from the incident, and pipes them through the actual Phase 2 `EventProcessor`. It captures state transitions and evaluates assertions.
- **Suite Engine:** Allows aggregating multiple `RegressionTest` executions.
- **Regression Proof:** A ledger proving a test failed BEFORE a fix and passed AFTER a fix.

---

## 3. Database Schema (Migration 005)

- `regression_tests`: Core definition storage using JSON DSL.
- `regression_test_versions`: History of changes.
- `regression_test_runs`: Execution logs and trace details.
- `regression_assertion_results`: Deep-dive into each assertion statement.
- `regression_proofs`: Tracks before/after status.
- `regression_suite_runs`: Aggregated executions.

---

## 4. Test DSL

A sample generated test definition:

```json
{
  "test_id": "REG-A1B2C3",
  "name": "duplicate_submission_incident",
  "initial_state": "IN_PROGRESS",
  "events": [
    { "type": "SESSION_STARTED" },
    { "type": "SUBMIT_REQUESTED" },
    { "type": "SUBMIT_REQUESTED" }
  ],
  "failure": {
    "type": "DUPLICATE",
    "target": "SUBMIT_REQUESTED"
  },
  "assertions": [
    { "path": "status", "operator": "EQUALS", "expected": "SUBMITTED" },
    { "path": "submission_count", "operator": "EQUALS", "expected": 1 }
  ]
}
```

---

## 5. Security and Limitations

- **No Arbitrary Code:** The system does NOT generate Python code. It generates a restricted JSON DSL. The Test Runner securely evaluates this DSL against predefined Domain models and Assertion paths.
- **Execution Isolation:** Tests run in memory using fresh UUIDs for sessions. They do not pollute the main production data (although they write to the same DB during execution, they use unique namespaces).
- **Determinism:** Tests run with fixed configurations to ensure they can reliably protect the system over time.

---

## 6. End-to-End Walkthrough

1. Go to **Failure Simulator** (Phase 3).
2. Inject a Duplicate `SUBMIT_REQUESTED` event. 
3. Simulator reports `State Corrupted (submission_count = 2)`.
4. Go to **Incidents** (Phase 4).
5. See `INC-XXXX` auto-detected. Open it.
6. Click **Create Regression Candidate**.
7. Go to **Regression Center** (Phase 5).
8. See Candidate under "Pending Candidates". Click **Generate Test**.
9. Test `REG-XXXX` is created. Open it.
10. Click **Run Test**.
11. Observe test FAIL (because the app logic is not yet fixed).
12. Application is fixed to ignore duplicate submits.
13. Click **Run Test** again.
14. Observe test PASS. 
15. Proof updates to `REGRESSION PROTECTED`.
