# [AI]: This file defines Pydantic models for entry-related operations.
# It provides schemas for creating, reading, updating, and deleting entries.
# Key features:
# - Base model for common entry fields
# - Separate models for create, read, update, and delete operations
# - ORM mode configuration for database integration

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

# [AI]: Base model for entry data, containing common fields
class EntryBase(BaseModel):
    content: str = Field(..., description="The content of the entry")

# [AI]: Model for creating a new entry
# Inherits from EntryBase without adding new fields
class EntryCreate(EntryBase):
    pass

# [AI]: Model for representing a complete entry, including database-generated fields
class Entry(EntryBase):
    id: int
    timestamp: datetime

    # [AI]: Enable ORM mode for easy conversion between ORM objects and Pydantic models
    class Config:
        orm_mode = True

# [AI]: Model for updating an existing entry
# Currently identical to EntryBase, but separated for potential future extensions
class EntryUpdate(EntryBase):
    pass

# [AI]: Model for deleting an entry, requiring only the entry's ID
class EntryDelete(BaseModel):
    id: int = Field(..., description="The ID of the deleted entry")