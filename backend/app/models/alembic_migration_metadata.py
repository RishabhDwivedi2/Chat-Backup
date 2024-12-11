# [AI]: This file implements the AlembicMigrationMetadata model.
# It provides functionality to track Alembic migration metadata in the database.
# Key features:
# - Defines a SQLAlchemy model for storing migration information
# - Tracks the timestamp and name of the last applied migration
# - Integrates with the project's base model class

from sqlalchemy import Column, Integer, DateTime, String
from .base import Base

class AlembicMigrationMetadata(Base):
    """
    [AI]: This class represents the Alembic migration metadata in the database.
    It stores information about the last applied migration, which is useful
    for tracking the database schema version and migration history.
    """
    __tablename__ = 'alembic_migration_metadata'

    # [AI]: Unique identifier for each metadata entry
    id = Column(Integer, primary_key=True)

    # [AI]: Timestamp of when the last migration was applied
    # The timezone=True parameter ensures that the timestamp is stored with timezone information
    last_migration_timestamp = Column(DateTime(timezone=True))

    # [AI]: Name or identifier of the last applied migration
    last_migration_name = Column(String)

# [AI]: Note: This model is likely used in conjunction with Alembic,
# a database migration tool for SQLAlchemy. It helps in tracking
# the state of database migrations, which is crucial for maintaining
# database schema consistency across different environments.
