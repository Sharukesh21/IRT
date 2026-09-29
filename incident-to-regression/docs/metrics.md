# Final Metric Definitions

This document defines the core metrics used to evaluate the Incident-to-Regression Pipeline.

### 1. Incident Detection Rate
- **Definition:** Percentage of benchmark failures successfully detected as incidents.
- **Formula:** `detected_incidents / injected_incidents × 100`
- **Data Source:** `evaluation_experiments` & `incidents`
- **Interpretation:** Measures the effectiveness of the Event Processor and Integrity Checker in identifying anomalous state transitions.
- **Limitations:** Only measures known failure classes within the benchmark dataset.

### 2. Reproduction Rate
- **Definition:** Success rate in synthesizing a deterministic failure configuration.
- **Formula:** `successfully_reproduced_incidents / reproducible_incidents × 100`
- **Data Source:** `evaluation_experiments` & `reproduction_specs`
- **Interpretation:** Indicates how reliably the Reproduction Engine can reverse-engineer the root cause from the timeline.
- **Limitations:** Excludes non-deterministic or environment-specific failures that cannot be safely reproduced in the test sandbox.

### 3. Test Generation Rate
- **Definition:** Ability to convert a reproduction candidate into an executable DSL regression test.
- **Formula:** `generated_regression_tests / regression_candidates × 100`
- **Data Source:** `regression_tests` & `evaluation_experiments`
- **Interpretation:** Measures the completeness of the DSL mapping layer.

### 4. Incident-to-Test Conversion Rate (End-to-End)
- **Definition:** The ultimate success rate of turning an initial production failure into a validated, CI-ready regression test.
- **Formula:** `incidents_producing_validated_tests / eligible_incidents × 100`
- **Data Source:** `evaluation_experiments` (Overall pipeline progression)
- **Interpretation:** Shows the holistic effectiveness of the entire pipeline.
- **Limitations:** Drops at any intermediate pipeline stage cumulatively affect this final score.

### 5. Regression Protection Rate
- **Definition:** The percentage of incidents that are currently guarded by at least one ACTIVE, passing regression test.
- **Formula:** `protected_incidents / eligible_incidents × 100`
- **Data Source:** `incidents` & `regression_tests`
- **Interpretation:** System-wide resilience metric.

### 6. Regression Escape Rate
- **Definition:** Rate at which an incident recurs in production despite having an active regression test.
- **Formula:** `escaped_incidents / protected_incidents × 100`
- **Data Source:** `regression_escapes`
- **Interpretation:** Identifies gaps in test coverage, flakiness, or assertion strictness.

### 7. Targeted Test Reduction
- **Definition:** Efficiency gain from executing only incident-relevant tests rather than the full suite.
- **Formula:** `1 - (targeted_tests / full_tests)`
- **Data Source:** `targeted_regression_evaluations`
- **Interpretation:** Higher is better, provided Protection Preservation remains at 100%.

### 8. Protection Preservation
- **Definition:** Ensures that running a targeted regression suite did not miss a failure that the full suite would have caught.
- **Formula:** `protected_targeted_incidents / protected_full_incidents × 100`
- **Data Source:** `targeted_regression_evaluations`
- **Interpretation:** Must be 100%. Anything less indicates the selector missed a relevant test.
