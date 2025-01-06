# app/routers/gmail_router.py

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import os
import base64
import logging
from app.config import settings
from email.mime.text import MIMEText
from app.database import get_db
import time
from datetime import datetime, timedelta
from app.routers.gateway_router import gmail_entry
from app.services.redis.redis_service import RedisService
from app.services.redis.token_manager import TokenManager

router = APIRouter()
logger = logging.getLogger(__name__)
redis_service = RedisService()
token_manager = TokenManager()

# Load Gmail OAuth client secrets from settings
CLIENT_CONFIG = {
    "web": {
        "client_id": settings.GMAIL.CLIENT_ID,
        "project_id": settings.GMAIL.PROJECT_ID,
        "auth_uri": settings.GMAIL.AUTH_URI,
        "token_uri": settings.GMAIL.TOKEN_URI,
        "client_secret": settings.GMAIL.CLIENT_SECRET,
        "redirect_uris": settings.GMAIL.REDIRECT_URIS,
        "javascript_origins": settings.GMAIL.JAVASCRIPT_ORIGINS,
    }
}

# OAuth2 scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send',
          "https://www.googleapis.com/auth/gmail.modify"]

# Add a processed message cache
last_processed_history_id = None
processed_messages = {}
CACHE_EXPIRY = timedelta(hours=24)
RATE_LIMIT_WINDOW = 5  # seconds

def clean_expired_messages():
    """Remove expired messages from the cache"""
    current_time = datetime.utcnow()
    expired = [msg_id for msg_id, timestamp in processed_messages.items() 
              if current_time - timestamp > CACHE_EXPIRY]
    for msg_id in expired:
        processed_messages.pop(msg_id, None)

async def get_gmail_service():
    """Get Gmail service with automatic token refresh"""
    try:
        # Get valid credentials using token manager
        credentials = await token_manager.get_valid_credentials(
            client_id=CLIENT_CONFIG['web']['client_id'],
            client_secret=CLIENT_CONFIG['web']['client_secret'],
            token_uri=CLIENT_CONFIG['web']['token_uri']
        )
        
        if not credentials:
            logger.error("No valid credentials available")
            raise HTTPException(
                status_code=401,
                detail="Gmail authentication required. Please authenticate at /auth/google"
            )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Test the credentials
        try:
            service.users().getProfile(userId='me').execute()
            return service
        except Exception as e:
            if 'invalid_grant' in str(e):
                # Clear invalid tokens
                await token_manager.clear_tokens()
                raise HTTPException(
                    status_code=401,
                    detail="Gmail authentication expired. Please re-authenticate at /auth/google"
                )
            raise
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating Gmail service: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Gmail authentication failed. Please re-authenticate at /auth/google"
        )

@router.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow with perpetual offline access"""
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
    )
    
    # Request offline access and force consent to ensure refresh token
    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Enable offline access
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return RedirectResponse(authorization_url)

@router.get("/auth/google/callback")
async def google_auth_callback(code: str, state: str):
    """Handle Google OAuth callback with token management"""
    try:
        logger.info("Received OAuth callback...")
        
        flow = Flow.from_client_config(
            CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=CLIENT_CONFIG['web']['redirect_uris'][0]
        )
        
        logger.info("Fetching token from Google...")
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        logger.info("Token fetched successfully, checking credentials...")
        logger.info(f"Access token present: {bool(credentials.token)}")
        logger.info(f"Refresh token present: {bool(credentials.refresh_token)}")
        logger.info(f"Expiry: {credentials.expiry}")
        
        if not credentials.refresh_token:
            logger.error("No refresh token received!")
            raise HTTPException(
                status_code=400,
                detail="Failed to obtain refresh token. Please try again."
            )

        # Store tokens using token manager
        logger.info("Attempting to store tokens...")
        stored = await token_manager.store_tokens(credentials)
        
        if not stored:
            logger.error("Failed to store tokens")
            raise HTTPException(status_code=500, detail="Failed to store authentication tokens")

        logger.info("Successfully stored new OAuth tokens")
        
        # Store additional metadata about the authentication
        auth_metadata = {
            'authenticated_at': datetime.utcnow().isoformat(),
            'scopes': credentials.scopes,
            'email': 'chatbot@resohub.ai'  # Updated to use your Gmail
        }
        
        await redis_service.store_value(
            'gmail_auth_metadata',
            json.dumps(auth_metadata),
            expiry_seconds=30 * 24 * 3600  # 30 days to match token expiry
        )

        return RedirectResponse(url="http://localhost:3001/auth-success")
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/status")
async def check_auth_status():
    """Check authentication status"""
    try:
        logger.info("Checking authentication status...")
        
        # Try to get tokens
        token_data = await token_manager._get_stored_tokens()
        
        if not token_data:
            return {
                "status": "unauthenticated",
                "message": "No authentication tokens found"
            }
            
        # Try to get valid credentials
        credentials = await token_manager.get_valid_credentials(
            client_id=CLIENT_CONFIG['web']['client_id'],
            client_secret=CLIENT_CONFIG['web']['client_secret'],
            token_uri=CLIENT_CONFIG['web']['token_uri']
        )
        
        if not credentials:
            return {
                "status": "invalid",
                "message": "Stored credentials are invalid"
            }
            
        return {
            "status": "authenticated",
            "expiry": token_data.get('expiry'),
            "scopes": token_data.get('scopes'),
            "created_at": token_data.get('created_at')
        }
        
    except Exception as e:
        logger.error(f"Error checking auth status: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/setup-gmail-watch")
async def setup_gmail_watch():
    """Setup Gmail push notifications"""
    try:
        # Change this line to await
        service = await get_gmail_service()
        
        request = {
            'labelIds': ['INBOX'],
            'topicName': f"projects/{settings.GMAIL.PROJECT_ID}/topics/gmail-notifications",
            'labelFilterAction': 'include'
        }
        
        response = service.users().watch(userId='me', body=request).execute()
        logger.info(f"Watch setup response: {response}")
        
        return {
            "message": "Gmail watch setup successful",
            "response": response
        }
        
    except Exception as e:
        logger.error(f"Error setting up Gmail watch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/watch-gmail")
async def setup_gmail_watch():
    """Setup Gmail watch with webhook URL"""
    try:
        service = get_gmail_service()
        
        webhook_url = "https://your-ngrok-url.ngrok-free.app/gmail-webhook"
        logger.info(f"Setting up Gmail watch with webhook URL: {webhook_url}")
        
        request = {
            'labelIds': ['INBOX'],
            'topicName': f"projects/{settings.GMAIL.PROJECT_ID}/topics/gmail-notifications",
            'labelFilterAction': 'include',
        }
        
        response = service.users().watch(userId='me', body=request).execute()
        logger.info(f"Watch setup response: {response}")
        
        return {
            "message": "Gmail watch setup successful",
            "response": response,
            "webhook_url": webhook_url
        }
        
    except Exception as e:
        logger.error(f"Error setting up Gmail watch: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def extract_email_body(msg):
    """Extract and clean email body"""
    body = ''
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body'].get('data', '')
                break
    else:
        body = msg['payload']['body'].get('data', '')

    if body:
        body = base64.urlsafe_b64decode(body).decode('utf-8')
        body_lines = body.split('\n')
        cleaned_body = []
        for line in body_lines:
            if line.strip().startswith('On ') and ' wrote:' in line:
                break
            cleaned_body.append(line)
        return '\n'.join(cleaned_body).strip()
    return ''

def extract_email_address(from_header):
    """Extract email address from From header"""
    return from_header.split('<')[1].strip('>') if '<' in from_header else from_header

def create_email_message(to: str, subject: str, body: str, thread_headers: dict = None):
    """Create an email message with proper headers for threading"""
    formatted_body = f"""Here's your AI response:

    {body}

    --
    This is an automated response"""

    message = MIMEText(formatted_body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = "chatbot@resohub.ai"
    
    new_message_id = f"<{int(time.time())}@gmail.com>"
    message['Message-ID'] = new_message_id
    
    if thread_headers:
        if thread_headers.get("message_id"):
            message['In-Reply-To'] = thread_headers["message_id"]
            
        references = thread_headers.get("references", "")
        if thread_headers.get("message_id"):
            if references:
                references = f"{references} {thread_headers['message_id']}"
            else:
                references = thread_headers["message_id"]
        
        if references:
            message['References'] = references
    
    return message

async def process_and_send_email_response(chat_response, email_metadata, service, db):
    """Process chat response and send email"""
    try:
        response_json = json.loads(chat_response.response)
        message_data = response_json.get("message", {})
        structured_response = message_data.get("structured_response", {})
        response_content = structured_response.get("content") if structured_response else message_data.get("content", "")

        if not response_content:
            response_content = "Sorry, I couldn't generate a response."

        message = create_email_message(
            to=email_metadata["from_email"],
            subject=f"Re: {email_metadata['subject']}" if email_metadata['thread_id'] else email_metadata['subject'],
            body=response_content,
            thread_headers={
                "message_id": email_metadata["message_id"],
                "references": email_metadata["references"],
                "thread_id": email_metadata["thread_id"]
            }
        )

        send_params = {
            'userId': 'me',
            'body': {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
        }
        
        if email_metadata['thread_id']:
            send_params['body']['threadId'] = email_metadata['thread_id']
        
        service.users().messages().send(**send_params).execute()
        logger.info(f"Successfully sent email response to {email_metadata['from_email']}")
        
    except Exception as e:
        logger.error(f"Error processing and sending email: {str(e)}")
        raise

@router.post("/gmail-webhook")
async def gmail_webhook(request: Request):
    """Gmail webhook with improved error handling, rate limiting, and token validation"""
    try:
        logger.info("\n=== NEW GMAIL WEBHOOK REQUEST ===")
        
        resource_state = request.headers.get('X-Goog-Resource-State')
        logger.info(f"Received notification type: {resource_state}")
        
        if resource_state in ['sync', 'exists']:
            logger.info("Received sync/exists notification, skipping processing")
            return {"status": "success", "message": "Sync notification acknowledged"}
        
        redis_health = await redis_service.get_health_status()
        
        if redis_health["status"] == "DOWN":
            logger.warning("⚠️ Gmail webhook running without Redis - duplicate processing possible")

        if await redis_service.get_rate_limit('gmail_webhook'):
            logger.info("Rate limit reached (Redis), skipping webhook")
            return {"status": "skipped", "reason": "rate_limit"}

        # Get Gmail service with automatic token refresh
        service = await get_gmail_service()
        
        messages = service.users().messages().list(
            userId='me', 
            maxResults=1,
            q='in:inbox -from:your-email@gmail.com'  # Replace with your email
        ).execute()

        if not messages.get('messages', []):
            return {"status": "success", "message": "No messages to process"}

        msg_id = messages['messages'][0]['id']
        
        if await redis_service.was_processed(msg_id):
            logger.info(f"Message {msg_id} already processed (Redis), skipping")
            return {"status": "skipped", "message": "Message already processed"}

        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
        message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)
        references = next((h['value'] for h in headers if h['name'] in ['References', 'In-Reply-To']), None)
        thread_id = msg.get('threadId')

        body = extract_email_body(msg)
        if not body:
            logger.info("No email body content found, skipping processing")
            return {"status": "skipped", "message": "No email content"}
            
        from_email = extract_email_address(from_header)

        email_metadata = {
            "email_id": msg_id,
            "thread_id": thread_id,
            "message_id": message_id,
            "references": references,
            "from_email": from_email,
            "subject": subject,
            "platform_metadata": {
                "max_tokens": 100,
                "temperature": 0.7
            }
        }

        db = next(get_db())
        
        test_user = {"sub": settings.APP.TEST_USER_EMAIL}
        chat_response = await gmail_entry(
            prompt=body,
            metadata=email_metadata,
            current_user=test_user,
            db=db,
            request=request
        )

        await process_and_send_email_response(
            chat_response=chat_response,
            email_metadata=email_metadata,
            service=service,
            db=db
        )

        await redis_service.set_processed(msg_id)
        
        return {"status": "success", "message": "Response sent"}

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in Gmail webhook: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        if "invalid_grant" in str(e):
            raise HTTPException(
                status_code=401,
                detail="Gmail authentication expired. Please re-authenticate at /auth/google"
            )
        return {"status": "error", "message": str(e)}

@router.post("/cleanup-gmail-webhook")
async def cleanup_gmail_webhook():
    """Clean up Gmail webhook and reset Redis"""
    try:
        redis_service.close()
        return {"message": "Gmail webhook cleaned up successfully"}
    except Exception as e:
        logger.error(f"Error in cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))