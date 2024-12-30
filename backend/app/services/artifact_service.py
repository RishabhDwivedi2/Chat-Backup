# app/services/artifact_service.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging
from typing import Optional, Dict, Any
from app.models.chat import Artifact, Message
from datetime import datetime
from .metadata.artifact_metadata import ArtifactMetadata, ComponentType, TableColumn, CardMetric

logger = logging.getLogger(__name__)

class ArtifactService:
    def __init__(self, db: Session):
        self.db = db

    # In ArtifactService
    async def create_artifact_from_parent_response(
        self,
        message_id: int,
        parent_response: Dict[str, Any]
    ) -> Optional[Artifact]:
        try:
            if not parent_response.get("has_artifact") or not parent_response.get("data"):
                return None

            component_type = parent_response.get("component_type")
            raw_data = parent_response.get("data")

            # Create metadata using new system
            metadata = ArtifactMetadata.from_raw_data(
                raw_data=raw_data,
                component_type=component_type,
                title=parent_response.get("title")
            )

            # Get presentation data
            presentation_data = metadata.get_presentation_data()

            new_artifact = Artifact(
                message_id=message_id,
                component_type=component_type,
                title=presentation_data["title"],
                description=parent_response.get("summary", ""),
                data=presentation_data["data"],
                style=presentation_data["visual"],
                configuration=presentation_data["config"]
            )

            self.db.add(new_artifact)
            self.db.commit()
            self.db.refresh(new_artifact)

            return new_artifact

        except Exception as e:
            logger.error(f"Error creating artifact: {str(e)}")
            self.db.rollback()
            raise

    def _convert_to_artifact_metadata(
        self,
        component_type: str,
        data: Dict[str, Any]
    ) -> ArtifactMetadata:
        """Convert raw data to proper artifact metadata structure"""
        try:
            if component_type == ComponentType.CHART:
                return ArtifactMetadata.create_chart_metadata(
                    title=data.get("title", "Chart"),
                    chart_type=data.get("type", "line"),
                    labels=data.get("labels", []),
                    datasets=data.get("datasets", []),
                    annotations=data.get("annotations"),
                    axes=data.get("axes")
                )
            elif component_type == ComponentType.TABLE:
                return ArtifactMetadata.create_table_metadata(
                    title=data.get("title", "Table"),
                    headers=[TableColumn(**h) if isinstance(h, dict) else h for h in data.get("headers", [])],
                    rows=data.get("rows", [])
                )
            elif component_type == ComponentType.CARD:
                return ArtifactMetadata.create_card_metadata(
                    title=data.get("title", "Card"),
                    metrics=[CardMetric(**m) if isinstance(m, dict) else m for m in data.get("metrics", [])]
                )
            else:
                raise ValueError(f"Unsupported component type: {component_type}")

        except Exception as e:
            logger.error(f"Error converting to artifact metadata: {str(e)}")
            raise

    def get_artifact(self, artifact_id: int) -> Artifact:
        """Retrieve an artifact by ID"""
        artifact = self.db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact

    def get_message_artifact(self, message_id: int) -> Optional[Artifact]:
        """Retrieve the artifact associated with a message"""
        return self.db.query(Artifact).filter(Artifact.message_id == message_id).first()