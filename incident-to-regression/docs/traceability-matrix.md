# Traceability Matrix

| Requirement | Phase | Feature | API / Domain | Database | UI / Frontend | Evidence |
|-------------|-------|---------|--------------|----------|---------------|----------|
| Online Exam Core | Phase 1 & 2 | Exam Engine, API, Processing | `exams.py`, `sessions.py`, `events.py` | `exams`, `students`, `sessions`, `events` | `/exam`, `/state-inspector` | Working exam state |
| Failure Simulation | Phase 3 | Chaos Testing, Network failure injection | `failure.py`, `failure_injector.py` | `failure_experiments`, `injected_events` | `/simulator` | Controlled event drops/dupes |
| Incident Intelligence | Phase 4 | Detection, Root Cause, Correlation | `incidents.py`, `incident_intelligence.py` | `incidents`, `incident_groups` | `/incidents` | Incident Timeline/Root Cause |
| Regression Automation | Phase 5 | Incident-to-Test Gen, Assertion Engine | `regression.py`, `test_generator.py`, `test_runner.py` | `regression_tests`, `regression_runs` | `/regression` | Executable DSL Tests |
| Production CI Integration | Phase 6 | Webhook, Ingestion, Orchestrator | `ci.py`, `ingestion.py`, `orchestrator.py` | `external_incidents`, `ci_regression_runs` | `/production-incidents`, `/ci-regression` | CI Gateway runs, DB records |
| Evaluation Framework | Phase 7 | Benchmarks, Experiment Engine, Metrics | `evaluation.py`, `evaluation_engine.py` | `evaluation_benchmarks`, `evaluation_experiments` | `/evaluation` | Real E2E benchmark runs |
| Targeted Test Selection | Phase 6 | `RegressionOrchestrator` scoring | `orchestrator.py` | `regression_plan_tests` | `/ci-regression` | Test Reduction % |
| Regression Escapes | Phase 6 | Re-ingestion detection on active tests | `orchestrator.py` | `regression_escapes` | `/ci-regression` | Escape Ledgers |
