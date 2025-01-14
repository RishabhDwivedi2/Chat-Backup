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

# JWT Configuration
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

# App Configuration
if 'APP' not in settings:
    settings['APP'] = {
        'TESTING_MODE': False
    }
logger.info(f"Testing Mode Status: {settings.APP.TESTING_MODE}")
logger.info(f"Test User Email: {settings.APP.TEST_USER_EMAIL}")

# Gmail Configuration
if 'GMAIL' not in settings:
    settings['GMAIL'] = {}

settings['GMAIL'].update(env_settings.get('GMAIL', {}))
settings['GMAIL'].update(secret_settings.get('GMAIL', {}))

# Ensure SMTP settings are properly initialized
if 'SMTP' not in settings['GMAIL']:
    settings['GMAIL']['SMTP'] = {}

# Update SMTP settings from environment and secret settings
if 'GMAIL' in env_settings and 'SMTP' in env_settings['GMAIL']:
    settings['GMAIL']['SMTP'].update(env_settings['GMAIL']['SMTP'])
if 'GMAIL' in secret_settings and 'SMTP' in secret_settings['GMAIL']:
    settings['GMAIL']['SMTP'].update(secret_settings['GMAIL']['SMTP'])

# Validate required SMTP settings
required_smtp_settings = ['EMAIL', 'PASSWORD', 'SERVER', 'PORT']
missing_settings = [setting for setting in required_smtp_settings 
                   if setting not in settings['GMAIL']['SMTP']]

if missing_settings:
    logger.error(f"Missing required SMTP settings: {', '.join(missing_settings)}")
    raise ValueError(f"Missing required SMTP settings: {', '.join(missing_settings)}")

# Google Workspace Configuration
if 'GOOGLE_WORKSPACE' not in settings:
    settings['GOOGLE_WORKSPACE'] = {}

settings['GOOGLE_WORKSPACE'].update(env_settings.get('GOOGLE_WORKSPACE', {}))
settings['GOOGLE_WORKSPACE'].update(secret_settings.get('GOOGLE_WORKSPACE', {}))

# Validate Google Workspace settings
required_workspace_settings = ['SERVICE_ACCOUNT_FILE', 'ADMIN_EMAIL', 'DOMAIN']
missing_workspace_settings = [setting for setting in required_workspace_settings
                            if setting not in settings['GOOGLE_WORKSPACE']]

if missing_workspace_settings:
    logger.error(f"Missing required Google Workspace settings: {', '.join(missing_workspace_settings)}")
    raise ValueError(f"Missing required Google Workspace settings: {', '.join(missing_workspace_settings)}")

# Validate service account file exists
service_account_path = Path(settings.GOOGLE_WORKSPACE.SERVICE_ACCOUNT_FILE)
if not service_account_path.is_absolute():
    service_account_path = PROJECT_ROOT / settings.GOOGLE_WORKSPACE.SERVICE_ACCOUNT_FILE

if not service_account_path.exists():
    logger.error(f"Service account file not found at: {service_account_path}")
    raise FileNotFoundError(f"Service account file not found at: {service_account_path}")

# Update the path to be absolute
settings.GOOGLE_WORKSPACE.SERVICE_ACCOUNT_FILE = str(service_account_path)

logger.info("Google Workspace configuration loaded successfully")
logger.info("Gmail SMTP configuration loaded successfully")