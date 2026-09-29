import uuid
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.regression_test import RegressionTest, RegressionTestVersion
from app.db.models.regression import RegressionCandidate, ReproductionSpec
from app.db.models.incident import Incident

class RegressionTestGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_from_candidate(self, candidate: RegressionCandidate, spec: ReproductionSpec, incident: Incident) -> RegressionTest:
        """Converts a regression candidate into a structured test definition."""
        
        # Build definition
        assertions = []
        
        # Convert expected state to assertions
        for path, value in spec.expected_state.items():
            assertions.append({
                "path": path,
                "operator": "EQUALS",
                "expected": value
            })
            
        definition = {
            "test_id": f"REG-{uuid.uuid4().hex[:6].upper()}",
            "name": f"{candidate.name.replace(' ', '_').lower()}",
            "initial_state": spec.initial_state,
            "events": spec.event_sequence,
            "failure": spec.failure_configuration,
            "assertions": assertions,
            "seed": spec.seed
        }
        
        test = RegressionTest(
            test_id=definition["test_id"],
            candidate_id=candidate.id,
            incident_id=incident.id,
            name=candidate.name,
            description=candidate.description,
            category=incident.category,
            failure_type=incident.failure_type,
            priority=candidate.priority,
            status="READY",
            test_definition=definition
        )
        self.db.add(test)
        await self.db.flush()
        
        version = RegressionTestVersion(
            test_id=test.id,
            version=1,
            definition=definition,
            change_reason="Initial Generation"
        )
        self.db.add(version)
        
        # Update candidate
        candidate.status = "IMPLEMENTED"
        
        await self.db.commit()
        return test
