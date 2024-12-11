# app/services/artifact_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
import logging
from typing import Optional, Dict, Any
from app.models.chat import Artifact, Message
from datetime import datetime

logger = logging.getLogger(__name__)

class ArtifactService:
    def __init__(self, db: Session):
        self.db = db

    async def create_artifact_from_parent_response(
        self,
        message_id: int,
        parent_response: Dict[str, Any]
    ) -> Optional[Artifact]:
        """
        Create an artifact from parent agent response if it contains artifact data
        """
        try:
            if not parent_response.get("has_artifact") or not parent_response.get("data"):
                return None

            artifact_data = parent_response.get("data", {})
            component_type = parent_response.get("component_type", "Chart")

            new_artifact = Artifact(
                message_id=message_id,
                component_type=component_type,
                title=artifact_data.get("title", "Untitled Artifact"),
                description=parent_response.get("summary", ""),
                data=artifact_data,
                style=artifact_data.get("style", {}),
                configuration={
                    "type": artifact_data.get("type", "default"),
                    "labels": artifact_data.get("labels", []),
                    "values": artifact_data.get("data", {}).get("values", [])
                }
            )

            message = self.db.query(Message).filter(Message.id == message_id).first()
            if not message:
                raise HTTPException(status_code=404, detail="Message not found")

            message.has_artifact = True

            # Add and commit
            self.db.add(new_artifact)
            self.db.commit()
            self.db.refresh(new_artifact)

            logger.info(f"Successfully created artifact {new_artifact.id} for message {message_id}")
            return new_artifact

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating artifact from parent response: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create artifact: {str(e)}"
            )

    def get_artifact(self, artifact_id: int) -> Artifact:
        """Retrieve an artifact by ID"""
        artifact = self.db.query(Artifact).filter(Artifact.id == artifact_id).first()
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact

    def get_message_artifact(self, message_id: int) -> Optional[Artifact]:
        """Retrieve the artifact associated with a message"""
        return self.db.query(Artifact).filter(Artifact.message_id == message_id).first()