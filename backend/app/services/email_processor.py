# # app/services/email_processor.py

# import base64
# from email.mime.text import MIMEText
# import logging
# import time

# logger = logging.getLogger(__name__)

# class EmailProcessor:
#     def __init__(self):
#         self.processed_messages = {}
        
#     def extract_email_details(self, msg):
#         headers = msg['payload']['headers']
#         return {
#             'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), ''),
#             'from_header': next((h['value'] for h in headers if h['name'] == 'From'), ''),
#             'message_id': next((h['value'] for h in headers if h['name'] == 'Message-ID'), None),
#             'references': next((h['value'] for h in headers if h['name'] in ['References', 'In-Reply-To']), None),
#             'thread_id': msg.get('threadId'),
#             'labels': msg.get('labelIds', [])
#         }

#     def extract_body(self, msg):
#         body = ''
#         if 'parts' in msg['payload']:
#             for part in msg['payload']['parts']:
#                 if part['mimeType'] == 'text/plain':
#                     body = part['body'].get('data', '')
#                     break
#         else:
#             body = msg['payload']['body'].get('data', '')

#         if not body:
#             return ''

#         body = base64.urlsafe_b64decode(body).decode('utf-8')
#         return self.clean_body(body)

#     def clean_body(self, body):
#         body_lines = body.split('\n')
#         cleaned_body = []
#         for line in body_lines:
#             if line.strip().startswith('On ') and ' wrote:' in line:
#                 break
#             cleaned_body.append(line)
#         return '\n'.join(cleaned_body).strip()

#     def create_response_email(self, to_email, subject, content, collection, message_id=None, references=None, thread_id=None):
#         email_body = f"""Here's your AI response:

# {content}

# --
# This response is part of conversation: {collection.collection_name}"""

#         message = MIMEText(email_body)
#         message['to'] = to_email
#         message['subject'] = subject
#         message['from'] = "rishabhdwivedi2002@gmail.com"
        
#         if message_id:
#             message['In-Reply-To'] = message_id
#             if references:
#                 message['References'] = f"{references} {message_id}".strip()
#             else:
#                 message['References'] = message_id

#         message['Message-ID'] = f"<{collection.id}-{int(time.time())}@gmail.com>"
        
#         return {
#             'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8'),
#             'threadId': thread_id
#         }
