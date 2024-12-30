# app/services/gmail_service.py

from app.config import settings
from google.auth.credentials import Credentials
from googleapiclient.discovery import build
from typing import Optional
from fastapi import Request
import base64
from email.mime.text import MIMEText
from typing import List
from fastapi import HTTPException

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

ACCESS_TOKEN = "ya29.a0ARW5m76ZMvJjZ0uFVrL5azuGAWByMv473ITSbh7qxmjpPaWFiAPuVeMfQxWbGJ20D9QxvSSk_8iYTR96LQQuIF2MuRkff3YAsEcXKwJ6lRdX16rGhUeiJRNGD56zxnnIOPwIF0hHp4X0im4ermiOmBV9bHgvEC8pnACAfFP8aCgYKAdsSARESFQHGX2Mi-hUg_t_k_iMfjZUHHKBt8A0175"  # Replace with your actual access token
REFRESH_TOKEN = "1//0gmbTZeAaMvQaCgYIARAAGBASNwF-L9IrwT1UjE9aRi4gpK7-MWtG-tLYh1Jn4h34Y07X1X94RIian8PpNopeyE2bhAzNwYhT78I"  # Replace with your actual refresh token

class GmailService:
    def __init__(self, user_email: str):
        self.user_email = user_email
        self.credentials = self._get_credentials()
        self.service = build('gmail', 'v1', credentials=self.credentials)

    def _get_credentials(self):
        return Credentials(
            token=ACCESS_TOKEN,
            refresh_token=REFRESH_TOKEN,
            token_uri=settings.GMAIL.TOKEN_URI,
            client_id=CLIENT_SECRETS['web']['client_id'],
            client_secret=CLIENT_SECRETS['web']['client_secret'],
        )

    async def extract_email_data(self, request: Request) -> dict:
        msg = await self._get_latest_message()
        return {
            "message_id": msg["id"],
            "thread_id": msg["threadId"],
            "from_email": self._extract_email_header(msg, "From"),
            "subject": self._extract_email_header(msg, "Subject"),
            "body": self._extract_email_body(msg),
            "attachments": self._extract_attachments(msg)
        }

    async def send_response(self, email_data: dict, response_content: str):
        message = self._create_email_message(
            to=email_data["from_email"],
            subject=f"Re: {email_data['subject']}",
            body=response_content,
            thread_id=email_data["thread_id"]
        )
        return self.service.users().messages().send(
            userId='me',
            body=message
        ).execute()
    # In gmail_service.py, add these methods:

    def _extract_email_header(self, msg: dict, header_name: str) -> str:
        headers = msg['payload']['headers']
        return next((h['value'] for h in headers if h['name'] == header_name), '')

    def _extract_email_body(self, msg: dict) -> str:
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

    def _extract_attachments(self, msg: dict) -> List[dict]:
        attachments = []
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part.get('filename'):
                    attachments.append({
                        'name': part['filename'],
                        'type': part['mimeType'],
                        'size': int(part['body'].get('size', 0)),
                        'attachmentId': part['body'].get('attachmentId')
                    })
        return attachments

    def _create_email_message(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> dict:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        message['from'] = self.user_email
        
        if thread_id:
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            return {
                'raw': raw,
                'threadId': thread_id
            }
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}

    async def _get_latest_message(self) -> dict:
        messages = self.service.users().messages().list(
            userId='me',
            maxResults=1,
            q='in:inbox -from:rishabhdwivedi2002@gmail.com'
        ).execute()

        if not messages.get('messages'):
            raise HTTPException(status_code=400, detail="No messages found")
            
        msg_id = messages['messages'][0]['id']
        return self.service.users().messages().get(userId='me', id=msg_id).execute()    