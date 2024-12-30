# app/routers/gmail_router.py

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
import os
from fastapi import Request
import base64
import logging
from app.config import settings  
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.chat_service import ChatService
from app.routers.chat_router import get_chat_response
import time
from datetime import datetime, timedelta
import asyncio
from app.routers.gateway_router import gmail_entry

router = APIRouter()
logger = logging.getLogger(__name__)

# Load Gmail OAuth client secrets from settings
CLIENT_SECRETS = {
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
          'https://www.googleapis.com/auth/gmail.send']

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

@router.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=CLIENT_SECRETS['web']['redirect_uris'][0]
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return RedirectResponse(authorization_url)

@router.get("/auth/google/callback")
async def google_auth_callback(code: str, state: str):
    """Handle Google OAuth callback"""
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=CLIENT_SECRETS['web']['redirect_uris'][0]
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials

    settings.GMAIL.TOKEN = credentials.token
    settings.GMAIL.REFRESH_TOKEN = credentials.refresh_token

    return RedirectResponse(url="http://localhost:3001/auth-success")

@router.post("/setup-gmail-watch")
async def setup_gmail_watch():
    try:
        credentials = Credentials(
            token=settings.GMAIL.ACCESS_TOKEN,
            refresh_token=settings.GMAIL.REFRESH_TOKEN,
            token_uri=settings.GMAIL.TOKEN_URI,
            client_id=CLIENT_SECRETS['web']['client_id'],
            client_secret=CLIENT_SECRETS['web']['client_secret'],
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Simpler watch request
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
    try:
        credentials = Credentials(
            token=settings.GMAIL.ACCESS_TOKEN,
            refresh_token=settings.GMAIL.REFRESH_TOKEN,
            token_uri=settings.GMAIL.TOKEN_URI,
            client_id=CLIENT_SECRETS['web']['client_id'],
            client_secret=CLIENT_SECRETS['web']['client_secret'],
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Add your ngrok URL
        webhook_url = "https://ff07-103-203-227-178.ngrok-free.app/gmail-webhook"
        logger.info(f"Setting up Gmail watch with webhook URL: {webhook_url}")
        
        request = {
            'labelIds': ['INBOX'],
            'topicName': f"projects/{settings.GMAIL.PROJECT_ID}/topics/gmail-notifications",
            'labelFilterAction': 'include',
        }
        
        logger.info(f"Watch request data: {request}")
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

@router.post("/gmail-webhook")
async def gmail_webhook(request: Request):
    """Modified Gmail webhook to use gateway flow"""
    try:
        logger.info("\n=== NEW GMAIL WEBHOOK REQUEST ===")
        
        # Rate limiting check
        current_time = time.time()
        last_process_time = getattr(gmail_webhook, 'last_process_time', 0)
        
        if current_time - last_process_time < RATE_LIMIT_WINDOW:
            logger.info("Rate limit reached, skipping webhook")
            return {"status": "skipped", "reason": "rate_limit"}
            
        gmail_webhook.last_process_time = current_time

        # Initialize Gmail service
        credentials = Credentials(
            token=settings.GMAIL.ACCESS_TOKEN,
            refresh_token=settings.GMAIL.REFRESH_TOKEN,
            token_uri=settings.GMAIL.TOKEN_URI,
            client_id=CLIENT_SECRETS['web']['client_id'],
            client_secret=CLIENT_SECRETS['web']['client_secret'],
        )
        
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get latest message
        messages = service.users().messages().list(
            userId='me', 
            maxResults=1,
            q='in:inbox -from:rishabhdwivedi2002@gmail.com'
        ).execute()

        if not messages.get('messages', []):
            return {"status": "success", "message": "No messages to process"}

        msg_id = messages['messages'][0]['id']
        
        # Check if message was already processed
        if msg_id in processed_messages:
            return {"status": "skipped", "message": "Message already processed"}

        # Process the message
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        
        # Extract email details
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
        message_id = next((h['value'] for h in headers if h['name'] == 'Message-ID'), None)
        references = next((h['value'] for h in headers if h['name'] in ['References', 'In-Reply-To']), None)
        thread_id = msg.get('threadId')

        # Extract and clean email body
        body = extract_email_body(msg)
        from_email = extract_email_address(from_header)

        # Prepare metadata for gateway
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

        # Get DB session
        db = next(get_db())
        
        # Use gateway flow
        test_user = {"sub": settings.APP.TEST_USER_EMAIL}
        chat_response = await gmail_entry(
            prompt=body,
            metadata=email_metadata,
            current_user=test_user,
            db=db,
            request=request
        )

        # Process response and send email
        await process_and_send_email_response(
            chat_response=chat_response,
            email_metadata=email_metadata,
            service=service,
            db=db
        )

        # Mark message as processed
        processed_messages[msg_id] = datetime.utcnow()
        
        return {"status": "success", "message": "Response sent"}

    except Exception as e:
        logger.error(f"Error in Gmail webhook: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        return {"status": "error", "message": str(e)}

# Helper functions
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
    """
    Create an email message with proper headers for threading
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        thread_headers: Dict containing message_id, references, and thread_id for threading
    """
    # Format email body with proper spacing
    formatted_body = f"""Here's your AI response:

    {body}

    --
    This is an automated response"""

    # Create email message
    message = MIMEText(formatted_body)
    message['to'] = to
    message['subject'] = subject
    message['from'] = "rishabhdwivedi2002@gmail.com"
    
    # Generate new Message-ID
    new_message_id = f"<{int(time.time())}@gmail.com>"
    message['Message-ID'] = new_message_id
    
    # Add threading headers if provided
    if thread_headers:
        if thread_headers.get("message_id"):
            message['In-Reply-To'] = thread_headers["message_id"]
            
        # Combine existing references with the message being replied to
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
    # Parse response
    response_json = json.loads(chat_response.response)
    message_data = response_json.get("message", {})
    structured_response = message_data.get("structured_response", {})
    response_content = structured_response.get("content") if structured_response else message_data.get("content", "")

    if not response_content:
        response_content = "Sorry, I couldn't generate a response."

    # Create email message
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

    # Send email
    send_params = {
        'userId': 'me',
        'body': {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
    }
    
    if email_metadata['thread_id']:
        send_params['body']['threadId'] = email_metadata['thread_id']
    
    service.users().messages().send(**send_params).execute()