import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.db.models.ci import ExternalIncident
from app.db.models.incident import Incident, IncidentGroup
from app.db.models.enums import IncidentStatus

class ExternalIncidentIngestor:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest(self, payload: dict) -> ExternalIncident:
        external_id = payload.get("external_incident_id", f"PROD-{uuid.uuid4().hex[:6].upper()}")
        
        # Check if already received
        res = await self.db.execute(select(ExternalIncident).where(ExternalIncident.external_incident_id == external_id))
        existing = res.scalars().first()
        if existing:
            return existing
            
        ext_incident = ExternalIncident(
            external_incident_id=external_id,
            source=payload.get("source", "PRODUCTION_API"),
            raw_payload=payload,
            status="RECEIVED"
        )
        self.db.add(ext_incident)
        await self.db.flush()
        
        # Normalize
        try:
            category = payload.get("category", "UNKNOWN")
            failure_type = payload.get("failure_type", "UNKNOWN")
            event_type = payload.get("event_type", "UNKNOWN")
            severity = payload.get("severity", "HIGH")
            
            # Deduplicate via fingerprinting
            fingerprint = f"{failure_type}:{event_type}"
            
            group_res = await self.db.execute(select(IncidentGroup).where(IncidentGroup.group_key == fingerprint))
            group = group_res.scalars().first()
            
            if not group:
                group = IncidentGroup(
                    group_key=fingerprint,
                    category=category,
                    failure_type=failure_type,
                    status=IncidentStatus.OPEN.value
                )
                self.db.add(group)
                await self.db.flush()
            else:
                group.occurrence_count += 1
                group.last_seen_at = func.now()
                
            incident = Incident(
                incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
                title=payload.get("title", f"{failure_type} in {event_type}"),
                description=payload.get("description", "External incident ingested."),
                severity=severity,
                category=category,
                failure_type=failure_type,
                primary_event_id=event_type,
                session_id=uuid.UUID(payload.get("session_id")) if payload.get("session_id") else uuid.uuid4(),
                experiment_id=uuid.uuid4(), # Faking experiment requirement for phase 4 structure
                group_id=group.id,
                occurred_at=datetime.utcnow()
            )
            self.db.add(incident)
            await self.db.flush()
            
            if not group.representative_incident_id:
                group.representative_incident_id = incident.id
            
            ext_incident.normalized_incident_id = incident.id
            ext_incident.status = "NORMALIZED"
            ext_incident.processed_at = func.now()
            
            await self.db.commit()
            
        except Exception as e:
            ext_incident.status = "ERROR"
            ext_incident.error = str(e)
            await self.db.commit()
            
        return ext_incident
