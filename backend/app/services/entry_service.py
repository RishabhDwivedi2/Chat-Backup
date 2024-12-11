# [AI]: This file implements entry-related database operations for a FastAPI backend.
# It provides functionality to create, read, update, and delete entries.
# Key features:
# - CRUD operations for entries
# - SQLAlchemy ORM integration
# - Error handling and logging
# - Pagination support for retrieving entries

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from backend.app.models.entry import Entry as EntryModel
from backend.app.schemas.entry import EntryCreate, EntryUpdate
import logging
from datetime import datetime

# [AI]: Set up logging for this module
logger = logging.getLogger(__name__)

# [AI]: Retrieve a list of entries with pagination support
def get_entries(db: Session, skip: int = 0, limit: int = 100) -> List[EntryModel]:
    return db.query(EntryModel).offset(skip).limit(limit).all()

# [AI]: Create a new entry in the database
def create_entry(db: Session, entry: EntryCreate):
    # [AI]: Log the received entry data for debugging purposes
    print(f"Received entry data: {entry}")
    
    # [AI]: Create a new EntryModel instance with the current UTC timestamp
    db_entry = EntryModel(content=entry.content, timestamp=datetime.utcnow())
    
    # [AI]: Add the new entry to the database, commit the transaction, and refresh the object
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

# [AI]: Retrieve a single entry by its ID
def get_entry(db: Session, entry_id: int) -> Optional[EntryModel]:
    return db.query(EntryModel).filter(EntryModel.id == entry_id).first()

# [AI]: Update an existing entry in the database
def update_entry(db: Session, entry_id: int, entry: EntryUpdate) -> Optional[EntryModel]:
    # [AI]: Attempt to retrieve the existing entry
    db_entry = get_entry(db, entry_id)
    if db_entry:
        try:
            # [AI]: Update only the fields provided in the EntryUpdate object
            for key, value in entry.dict(exclude_unset=True).items():
                setattr(db_entry, key, value)
            
            # [AI]: Commit the changes and refresh the entry object
            db.commit()
            db.refresh(db_entry)
            logger.info(f"Updated entry with id: {entry_id}")
            return db_entry
        except SQLAlchemyError as e:
            # [AI]: Log any database errors and roll back the transaction
            logger.error(f"Error updating entry {entry_id}: {str(e)}")
            db.rollback()
            raise
    # [AI]: Log a warning if the entry to be updated was not found
    logger.warning(f"Entry with id {entry_id} not found for update")
    return None

# [AI]: Delete an entry from the database
def delete_entry(db: Session, entry_id: int) -> Optional[EntryModel]:
    # [AI]: Attempt to retrieve the existing entry
    db_entry = get_entry(db, entry_id)
    if db_entry:
        try:
            # [AI]: Delete the entry and commit the transaction
            db.delete(db_entry)
            db.commit()
            logger.info(f"Deleted entry with id: {entry_id}")
            return db_entry
        except SQLAlchemyError as e:
            # [AI]: Log any database errors and roll back the transaction
            logger.error(f"Error deleting entry {entry_id}: {str(e)}")
            db.rollback()
            raise
    # [AI]: Log a warning if the entry to be deleted was not found
    logger.warning(f"Entry with id {entry_id} not found for deletion")
    return None