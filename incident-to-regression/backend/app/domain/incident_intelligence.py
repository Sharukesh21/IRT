import uuid
import hashlib
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.incident import (
    Incident, IncidentGroup, IncidentEvidence, IncidentTimeline, 
    IncidentRootCause, IncidentExpectation
)
from app.db.models.failure import FailureExperiment, IntegrityResult, FailureScenario, InjectedEvent
from app.db.models.enums import IncidentStatus, EvidenceType
from app.db.models.regression import ReproductionSpec

class IncidentIntelligence:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_incident(self, detection: Dict[str, Any]) -> Incident:
        experiment: FailureExperiment = detection["experiment"]
        integrity: IntegrityResult = detection["integrity"]
        scenario: FailureScenario = detection["scenario"]
        severity = detection["severity"]
        category = detection["category"]
        
        # 1. Deduplication / Grouping
        fingerprint = self._generate_fingerprint(category.value, scenario.failure_type.name, scenario.target_event_type, integrity.violations)
        group = await self._get_or_create_group(fingerprint, category.value, scenario.failure_type.name)
        
        # 2. Create Incident Record
        incident_id_str = f"INC-{uuid.uuid4().hex[:6].upper()}"
        incident = Incident(
            incident_id=incident_id_str,
            title=detection["title"],
            description=f"Automatically captured incident from experiment {experiment.id}",
            status=IncidentStatus.OPEN.value,
            severity=severity.value,
            category=category.value,
            failure_type=scenario.failure_type.name,
            session_id=experiment.session_id,
            experiment_id=experiment.id,
            group_id=group.id,
            primary_event_id=scenario.target_event_type,
            occurred_at=experiment.started_at,
            reproducible=True, # We have the experiment params
            state_corrupted=experiment.state_corrupted,
            recovery_status=experiment.recovery_status.name if hasattr(experiment.recovery_status, 'name') else str(experiment.recovery_status)
        )
        self.db.add(incident)
        await self.db.flush() # get ID
        
        # Update group
        group.occurrence_count += 1
        group.last_seen_at = experiment.completed_at
        if not group.representative_incident_id:
            group.representative_incident_id = incident.id
            
        # 3. Create Evidence
        await self._create_evidence(incident.id, experiment, integrity, scenario)
        
        # 4. Create Expectations
        exp = IncidentExpectation(
            incident_id=incident.id,
            expected_state={"status": integrity.expected_state},
            actual_state={"status": integrity.actual_state, "submission_count": integrity.submission_count},
            invariant_violations=integrity.violations
        )
        self.db.add(exp)
        
        # 5. Build Timeline
        await self._build_timeline(incident.id, experiment.id)
        
        # 6. Root Cause
        self._determine_root_cause(incident.id, scenario, integrity.violations)
        
        # 7. Reproduction Spec
        await self._create_reproduction_spec(incident.id, experiment, scenario, integrity)
        
        await self.db.commit()
        return incident

    def _generate_fingerprint(self, category: str, failure_type: str, target_event: str, violations: List[str]) -> str:
        # e.g. DUPLICATION:DUPLICATE:SUBMIT_REQUESTED:Multiple confirmed submissions detected.
        violation_str = violations[0] if violations else "UNKNOWN"
        raw = f"{category}:{failure_type}:{target_event}:{violation_str}"
        return hashlib.md5(raw.encode()).hexdigest()

    async def _get_or_create_group(self, fingerprint: str, category: str, failure_type: str) -> IncidentGroup:
        res = await self.db.execute(select(IncidentGroup).where(IncidentGroup.group_key == fingerprint))
        group = res.scalars().first()
        if not group:
            group = IncidentGroup(
                group_key=fingerprint,
                category=category,
                failure_type=failure_type
            )
            self.db.add(group)
            await self.db.flush()
        return group
        
    async def _create_evidence(self, incident_id: uuid.UUID, exp: FailureExperiment, intg: IntegrityResult, scen: FailureScenario):
        ev1 = IncidentEvidence(
            incident_id=incident_id,
            evidence_type=EvidenceType.EXPERIMENT.value,
            source_id=str(exp.id),
            payload={"event_count": exp.event_count, "processing_time_ms": exp.processing_time_ms}
        )
        ev2 = IncidentEvidence(
            incident_id=incident_id,
            evidence_type=EvidenceType.FAILURE_INJECTION.value,
            source_id=str(scen.id),
            payload={"failure_type": scen.failure_type.name, "target": scen.target_event_type, "params": scen.parameters}
        )
        self.db.add_all([ev1, ev2])

    async def _build_timeline(self, incident_id: uuid.UUID, experiment_id: uuid.UUID):
        res = await self.db.execute(select(InjectedEvent).where(InjectedEvent.experiment_id == experiment_id).order_by(InjectedEvent.delivery_sequence))
        injected_events = res.scalars().all()
        
        for ev in injected_events:
            is_anomaly = ev.failure_type.name != "NONE" if hasattr(ev.failure_type, 'name') else str(ev.failure_type) != "NONE"
            tl = IncidentTimeline(
                incident_id=incident_id,
                event_id=ev.injected_event_id,
                sequence=ev.delivery_sequence,
                event_type=ev.modification or "EVENT",
                occurred_at=ev.occurred_at,
                received_at=ev.received_at,
                processing_status=ev.status,
                is_anomalous=is_anomaly,
                failure_type=ev.failure_type.name if hasattr(ev.failure_type, 'name') else str(ev.failure_type)
            )
            self.db.add(tl)
            
    def _determine_root_cause(self, incident_id: uuid.UUID, scenario: FailureScenario, violations: List[str]):
        cause_code = "UNKNOWN"
        explanation = "Unable to determine root cause deterministicly."
        
        ft = scenario.failure_type.name if hasattr(scenario.failure_type, 'name') else str(scenario.failure_type)
        if "DUPLICATE" in ft and any("Multiple confirmed submissions" in v for v in violations):
            cause_code = "DUPLICATE_SIDE_EFFECT"
            explanation = "The same logical operation was processed more than once, resulting in multiple side effects. Idempotency checks failed to catch the duplicate."
        elif "ORDER" in ft:
            cause_code = "ORDERING_VIOLATION"
            explanation = "Events were processed out of logical order, causing state corruption."
            
        rc = IncidentRootCause(
            incident_id=incident_id,
            cause_code=cause_code,
            explanation=explanation
        )
        self.db.add(rc)
        
    async def _create_reproduction_spec(self, incident_id: uuid.UUID, exp: FailureExperiment, scen: FailureScenario, intg: IntegrityResult):
        spec = ReproductionSpec(
            reproduction_id=f"REP-{uuid.uuid4().hex[:6].upper()}",
            incident_id=incident_id,
            initial_state=exp.initial_state,
            failure_configuration={
                "type": scen.failure_type.name if hasattr(scen.failure_type, 'name') else str(scen.failure_type),
                "target": scen.target_event_type,
                "params": scen.parameters
            },
            expected_state={"status": intg.expected_state, "submission_count": 1},
            expected_outcome="CORRUPTED" if exp.state_corrupted else "RECOVERED"
        )
        self.db.add(spec)
