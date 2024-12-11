from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import sys
from pathlib import Path
import importlib
from app.config import settings

# Add the project root and backend directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(BACKEND_DIR))

from app.models.base import Base

# Dynamically import all models
models_path = BACKEND_DIR / "app" / "models"
for model_file in models_path.glob("*.py"):
    if model_file.stem not in ["__init__", "base"]:
        importlib.import_module(f"app.models.{model_file.stem}")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE.URL)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = settings.DATABASE.URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE.URL
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()