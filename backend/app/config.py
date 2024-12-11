# app/config.py

import os
from pathlib import Path
from dynaconf import Dynaconf
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parents[2]
config_dir = PROJECT_ROOT / "backend" / "config"

base_settings = Dynaconf(settings_files=[str(config_dir / "settings.toml")])
env_settings = Dynaconf(settings_files=[str(config_dir / f"settings.{os.environ.get('ENV', 'lcl')}.toml")])
secret_settings = Dynaconf(settings_files=[str(config_dir / ".secrets.lcl.toml")])

settings = Dynaconf()
settings.update(base_settings.as_dict())
settings.update(env_settings.as_dict())
settings.update(secret_settings.as_dict())

# Ensure JWT settings are available
if 'JWT' not in settings:
    settings['JWT'] = {
        'SECRET_KEY': settings.get('SECRET_KEY', {}).get('SECRET_KEY'),
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': 1440
    }

# Convert SECRET_KEY to string if it exists
if 'SECRET_KEY' in settings.JWT:
    settings.JWT.SECRET_KEY = str(settings.JWT.SECRET_KEY)
    logger.debug(f"JWT SECRET_KEY set as string. Type: {type(settings.JWT.SECRET_KEY)}")
else:
    logger.error("JWT SECRET_KEY is not set in the configuration files")
    raise ValueError("JWT SECRET_KEY is not set in the configuration files")

# Database configuration
if 'DATABASE' not in settings:
    settings['DATABASE'] = {}

settings['DATABASE'].update(env_settings.get('DATABASE', {}))
settings['DATABASE'].update(secret_settings.get('DATABASE', {}))

db_host = settings.DATABASE.HOST
db_port = settings.DATABASE.PORT
db_name = settings.DATABASE.NAME
db_user = settings.DATABASE.USER_NAME
db_password = secret_settings.DATABASE.USER_PASSWORD

settings.DATABASE.URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

logger.debug(f"JWT Algorithm: {settings.JWT.ALGORITHM}")
logger.debug(f"JWT Token expiration: {settings.JWT.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")