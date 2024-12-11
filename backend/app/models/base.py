# [AI]: This file implements the base configuration for SQLAlchemy ORM models.
# It provides functionality to create a base class for declarative models.
# Key features:
# - Creates a declarative base for SQLAlchemy models
# - Centralizes the base configuration for all models in the application

from sqlalchemy.ext.declarative import declarative_base

# [AI]: Create a base class for declarative models
# This base class will be used by all other model classes in the application
# to inherit common SQLAlchemy functionality and metadata
Base = declarative_base()

# [AI]: The file ends here. Typically, additional model classes would be
# defined in separate files, inheriting from this Base class.
