# backend/app/utils/schema_generator.py

from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from app.models.user import User
from app.models.chat import ChatCollection, Conversation, Message, Attachment, Artifact
import logging

logger = logging.getLogger(__name__)

def generate_schema():
    try:
        # Create a dummy engine (just for schema generation)
        engine = create_engine('postgresql://')
        
        models = [User, ChatCollection, Conversation, Message, Attachment, Artifact]
        
        schema = ""
        for model in models:
            schema += str(CreateTable(model.__table__).compile(engine)) + ";\n\n"
        
        # Save to a file in your project root
        with open('schema.sql', 'w') as f:
            f.write(schema)
            
        logger.info("Schema generated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error generating schema: {str(e)}")
        return False