# migrations/env.py

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine, MetaData
from alembic import context
from app.database import Base
from backend.app.config.constants import settings
from app.models import *

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# List of schemas/tables to ignore
IGNORED_SCHEMAS = {'auth', 'storage', 'pg_', 'realtime', 'vault'}
IGNORED_TABLES = {
    'auth.users', 'auth.schema_migrations', 'auth.refresh_tokens',
    'storage.buckets', 'storage.objects', 'realtime.subscription'
}

def get_table_name(obj):
    """Safely get table name from an object"""
    if hasattr(obj, 'table') and hasattr(obj.table, 'name'):
        return obj.table.name
    elif hasattr(obj, 'name'):
        return obj.name
    return None

def should_include_object(name, type_):
    """Determine if an object should be included in migrations"""
    # Ignore objects in system schemas
    if any(name.startswith(f"{schema}.") for schema in IGNORED_SCHEMAS):
        return False
    
    # Ignore specific system tables
    if name in IGNORED_TABLES:
        return False
        
    return True

def include_object(object, name, type_, reflected, compare_to):
    """Filter objects for migration"""
    
    # Always ignore system schemas/tables
    if not should_include_object(name, type_):
        return False

    # For tables
    if type_ == "table":
        # Only include tables that exist in our SQLAlchemy models
        return name in [model.__tablename__ for model in Base.__subclasses__()]
        
    # For columns and other objects
    if type_ == "column":
        table_name = get_table_name(object)
        if table_name:
            # Only include columns from tables in our models
            return table_name in [model.__tablename__ for model in Base.__subclasses__()]
    
    return False

target_metadata = Base.metadata

def process_revision_directives(context, revision, directives):
    """Prevent unintended table drops"""
    if directives[0].upgrade_ops.ops:
        # Remove any drop_table operations
        final_ops = []
        for op in directives[0].upgrade_ops.ops:
            if not hasattr(op, 'table_name') or op.table_name == 'temp_test':
                final_ops.append(op)
        directives[0].upgrade_ops.ops = final_ops

def run_migrations_offline() -> None:
    url = settings.DATABASE.URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=include_object,
        process_revision_directives=process_revision_directives,
        compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = create_engine(
        settings.DATABASE.URL,
        pool_pre_ping=True,
        connect_args={
            "sslmode": "require",
        }
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            process_revision_directives=process_revision_directives,
            compare_type=True,
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()