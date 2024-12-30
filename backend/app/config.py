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

if 'JWT' not in settings:
    settings['JWT'] = {
        'SECRET_KEY': settings.get('SECRET_KEY', {}).get('SECRET_KEY'),
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': 1440
    }

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

# Construct PostgreSQL URL
DATABASE_URL = (
    f"postgresql://{settings.DATABASE.USER_NAME}:{settings.DATABASE.PASSWORD}"
    f"@{settings.DATABASE.HOST}:{settings.DATABASE.PORT}/{settings.DATABASE.NAME}"
    f"?sslmode={settings.DATABASE.get('SSL_MODE', 'disable')}"
)
settings.DATABASE.URL = DATABASE_URL

logger.info(f"Database URL configured for local PostgreSQL")

if 'APP' not in settings:
    settings['APP'] = {
        'TESTING_MODE': False  # Default to False
    }
logger.info(f"Testing Mode Status: {settings.APP.TESTING_MODE}")
logger.info(f"Test User Email: {settings.APP.TEST_USER_EMAIL}")

# Gmail Configuration
if 'GMAIL' not in settings:
    settings['GMAIL'] = {}

settings['GMAIL'].update(env_settings.get('GMAIL', {}))
settings['GMAIL'].update(secret_settings.get('GMAIL', {}))


    