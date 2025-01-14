# app/services/google_workspace_service.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import logging
from typing import Optional
from datetime import datetime
import time
from app.config import settings

logger = logging.getLogger(__name__)

class GoogleWorkspaceService:
    def __init__(self):
        self.SCOPES = [
            'https://www.googleapis.com/auth/admin.directory.user',
            'https://www.googleapis.com/auth/gmail.settings.basic',
            'https://www.googleapis.com/auth/gmail.settings.sharing',
            'https://www.googleapis.com/auth/admin.directory.orgunit',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://mail.google.com/',
            'https://www.googleapis.com/auth/gmail.settings.basic',
            'https://www.googleapis.com/auth/admin.directory.user.security'
        ]
        self.DOMAIN = "resohub.ai"
        self.FORWARD_TO = "chatbot@resohub.ai"
        self.admin_service = None
        self.gmail_service = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize the Google Workspace and Gmail services with service account credentials"""
        try:
            # Create base credentials with all required scopes
            self.credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_WORKSPACE.SERVICE_ACCOUNT_FILE,
                scopes=self.SCOPES,
                subject='chatbot@resohub.ai'  
            )
            
            self.admin_service = build('admin', 'directory_v1', credentials=self.credentials)
            self.gmail_service = build('gmail', 'v1', credentials=self.credentials)
            
            logger.info("Successfully initialized Google Workspace and Gmail services")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise

    async def setup_email_forwarding(self, email: str) -> bool:
        """Set up email forwarding using multiple methods"""
        try:
            # Wait for account provisioning
            time.sleep(5)

            add_forward = {
                'forwardingEmail': self.FORWARD_TO
            }

            new_user_credentials = self.credentials.with_subject(email)
            new_user_gmail = build('gmail', 'v1', credentials=new_user_credentials)

            try:
                new_user_gmail.users().settings().forwardingAddresses().create(
                    userId='me',
                    body=add_forward
                ).execute()

                # Wait for forwarding address to be registered
                time.sleep(2)

                # Enable forwarding
                enable_forwarding = {
                    'emailAddress': self.FORWARD_TO,
                    'enabled': True,
                    'disposition': 'leaveInInbox'
                }

                new_user_gmail.users().settings().updateAutoForwarding(
                    userId='me',
                    body=enable_forwarding
                ).execute()

                filter_content = {
                    'criteria': {
                        'from': '*'  
                    },
                    'action': {
                        'forward': self.FORWARD_TO
                    }
                }

                new_user_gmail.users().settings().filters().create(
                    userId='me',
                    body=filter_content
                ).execute()

                logger.info(f"Successfully set up email forwarding for {email}")
                return True

            except Exception as gmail_error:
                logger.warning(f"Gmail API forwarding setup failed: {str(gmail_error)}")

                # Try alternative method using Admin SDK
                try:
                    # Grant super admin temporary access
                    delegate_body = {
                        'delegationRequests': [{
                            'emailAddress': self.FORWARD_TO,
                            'status': 'PENDING'
                        }]
                    }

                    self.admin_service.users().update(
                        userKey=email,
                        body={
                            'email': email,
                            'isMailboxSetup': True,
                            'settings': {
                                'automaticForwarding': {
                                    'autoForwardingEnabled': True,
                                    'emailAddress': self.FORWARD_TO,
                                    'disposition': 'leaveInInbox'
                                }
                            }
                        }
                    ).execute()

                    logger.info(f"Successfully set up forwarding via Admin SDK for {email}")
                    return True

                except Exception as admin_error:
                    logger.error(f"Admin SDK forwarding setup failed: {str(admin_error)}")
                    raise admin_error

        except Exception as e:
            error_details = str(e)
            if hasattr(e, 'response'):
                try:
                    error_details = e.response.text
                except:
                    pass
            logger.error(f"Failed to set up email forwarding for {email}. Details: {error_details}")
            return False

    async def create_workspace_user(self, first_name: str, last_name: str, company_name: str) -> Optional[dict]:
        """Create a new Google Workspace user account with email forwarding"""
        try:
            email_prefix = ''.join(e.lower() for e in company_name if e.isalnum())
            email = f"{email_prefix}@{self.DOMAIN}"
            
            try:
                self.admin_service.users().get(userKey=email).execute()
                email = f"{email_prefix}{int(time.time())}@{self.DOMAIN}"
            except Exception as e:
                if "404" not in str(e):
                    raise
                pass
                    
            logger.info(f"Generated unique email: {email}")

            user_data = {
                'name': {
                    'givenName': first_name,
                    'familyName': last_name
                },
                'password': self._generate_temporary_password(),
                'primaryEmail': email,
                'changePasswordAtNextLogin': True,
                'orgUnitPath': '/',
            }

            # Create user with single retry
            try:
                created_user = self.admin_service.users().insert(body=user_data).execute()
                logger.info(f"Successfully created Workspace user: {email}")
            except Exception as e:
                if "Entity already exists" in str(e):
                    email = f"{email_prefix}{int(time.time())}@{self.DOMAIN}"
                    user_data['primaryEmail'] = email
                    created_user = self.admin_service.users().insert(body=user_data).execute()
                    logger.info(f"Successfully created Workspace user on retry: {email}")
                else:
                    raise

            # Set up email forwarding
            forwarding_success = await self.setup_email_forwarding(email)
            if not forwarding_success:
                logger.warning(f"Email forwarding setup failed for {email}")

            return {
                'email': email,
                'created_at': datetime.utcnow().isoformat(),
                'status': 'success',
                'forwarding_setup': forwarding_success
            }

        except Exception as e:
            logger.error(f"Failed to create Workspace user: {str(e)}")
            return None

    def _generate_temporary_password(self) -> str:
        """Generate a secure temporary password"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(16))
        
        # Ensure password meets Google's requirements
        password = f"Welcome{password}2024!"
        return password

    async def delete_workspace_user(self, email: str) -> bool:
        """Delete a Google Workspace user account completely"""
        try:
            self.admin_service.users().delete(userKey=email).execute()
            logger.info(f"Successfully deleted Workspace user: {email}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete Workspace user {email}: {str(e)}")
            return False