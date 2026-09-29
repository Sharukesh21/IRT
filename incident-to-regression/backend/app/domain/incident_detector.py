import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.failure import FailureExperiment, IntegrityResult, InjectedEvent, FailureScenario
from app.db.models.incident import Incident, IncidentStatus, IncidentGroup
from app.db.models.enums import IncidentSeverity, IncidentCategory

class IncidentDetector:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def detect_from_experiment(self, experiment_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Evaluates an experiment and determines if a meaningful failure occurred.
        Returns the incident payload if detected, otherwise None.
        """
        # Fetch experiment and integrity result
        exp_res = await self.db.execute(select(FailureExperiment).where(FailureExperiment.id == experiment_id))
        experiment = exp_res.scalars().first()
        
        if not experiment:
            return None
            
        int_res = await self.db.execute(select(IntegrityResult).where(IntegrityResult.experiment_id == experiment_id))
        integrity = int_res.scalars().first()
        
        scen_res = await self.db.execute(select(FailureScenario).where(FailureScenario.id == experiment.scenario_id))
        scenario = scen_res.scalars().first()
        
        if not integrity or not scenario:
            return None

        # --- RULES ---
        is_incident = False
        severity = IncidentSeverity.LOW
        category = IncidentCategory.UNKNOWN
        
        # Rule 1 & 2: State Corruption or Integrity Failure
        if experiment.state_corrupted or integrity.status == "FAILED":
            is_incident = True
            severity = IncidentSeverity.HIGH
            
            # Refine severity based on specific violations
            for v in integrity.violations:
                if "Multiple confirmed submissions" in v:
                    severity = IncidentSeverity.CRITICAL
                    category = IncidentCategory.DATA_INTEGRITY
                elif "Invalid state regression" in v:
                    severity = IncidentSeverity.HIGH
                    category = IncidentCategory.STATE_MACHINE

        # If it's a recovered failure, it's not automatically an incident
        if not is_incident:
            return None
            
        # Determine category based on failure type if not set by specific violations
        if category == IncidentCategory.UNKNOWN:
            ft = scenario.failure_type.name if hasattr(scenario.failure_type, 'name') else str(scenario.failure_type)
            if "DUPLICATE" in ft:
                category = IncidentCategory.DUPLICATION
            elif "ORDER" in ft:
                category = IncidentCategory.EVENT_ORDERING
            elif "TIMEOUT" in ft or "RETRY" in ft:
                category = IncidentCategory.TIMEOUT
            elif "DELAY" in ft:
                category = IncidentCategory.EVENT_PROCESSING
        
        title = f"State Corruption during {scenario.failure_type}"
        if severity == IncidentSeverity.CRITICAL:
            title = f"CRITICAL: {title}"
            
        return {
            "experiment": experiment,
            "integrity": integrity,
            "scenario": scenario,
            "severity": severity,
            "category": category,
            "title": title
        }
