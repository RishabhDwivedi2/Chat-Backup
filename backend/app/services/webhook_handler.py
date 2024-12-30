# # app/services/webhook_handler.py

# import logging
# from app.services.chat_service import ChatService
# from app.routers.chat_router import get_chat_response
# import json
# from datetime import datetime, timedelta

# logger = logging.getLogger(__name__)

# class WebhookHandler:
#     def __init__(self, gmail_service, email_processor, db, test_user):
#         self.gmail_service = gmail_service
#         self.email_processor = email_processor
#         self.db = db
#         self.test_user = test_user
#         self.chat_service = ChatService(db)
        
#     async def process_webhook(self, msg_id):
#         msg = self.gmail_service.get_latest_message()
#         if not msg:
#             return {"status": "success", "message": "No messages to process"}

#         email_details = self.email_processor.extract_email_details(msg)
        
#         if self.should_skip_message(email_details):
#             return {"status": "skipped", "reason": "Skip condition met"}

#         body = self.email_processor.extract_body(msg)
#         if not body:
#             return {"status": "skipped", "reason": "no body"}

#         from_email = self.extract_from_email(email_details['from_header'])
        
#         conversation_data = await self.process_conversation(
#             body, 
#             email_details['subject'],
#             email_details['thread_id']
#         )
        
#         if not conversation_data:
#             return {"status": "error", "message": "Failed to process conversation"}

#         email_data = self.email_processor.create_response_email(
#             to_email=from_email,
#             subject=conversation_data['subject'],
#             content=conversation_data['content'],
#             collection=conversation_data['collection'],
#             message_id=email_details['message_id'],
#             references=email_details['references'],
#             thread_id=email_details['thread_id'] if conversation_data['is_reply'] else None
#         )

#         self.gmail_service.send_email(email_data, email_details['thread_id'])
#         return {"status": "success", "message": "Response sent"}

#     def should_skip_message(self, email_details):
#         return any([
#             'DRAFT' in email_details['labels'],
#             'SENT' in email_details['labels'],
#             not email_details['subject'],
#             'rishabhdwivedi2002@gmail.com' in email_details['from_header']
#         ])

#     def extract_from_email(self, from_header):
#         return from_header.split('<')[1].strip('>') if '<' in from_header else from_header

#     async def process_conversation(self, body, subject, thread_id):
#         try:
#             original_subject = subject[3:].strip() if subject.lower().startswith('re:') else subject
            
#             conversation_id = None
#             existing_collection = None
            
#             if thread_id:
#                 conversation_id = self.chat_service.get_collection_and_first_conversation(
#                     user_email=self.test_user["sub"],
#                     subject=original_subject
#                 )
#                 if conversation_id:
#                     conversation = self.chat_service.get_conversation(conversation_id)
#                     existing_collection = self.chat_service.get_collection_by_name(
#                         self.test_user["sub"], 
#                         conversation.title
#                     )

#             chat_response = await get_chat_response(
#                 prompt=body,
#                 max_tokens=100,
#                 temperature=0.7,
#                 conversation_id=conversation_id,
#                 parent_message_id=None,
#                 attachments=None,
#                 current_user=self.test_user,
#                 db=self.db
#             )

#             response_json = json.loads(chat_response.response)
#             message_data = response_json.get("message", {})
#             structured_response = message_data.get("structured_response", {})
#             content = structured_response.get("content") if structured_response else message_data.get("content", "")
            
#             if not content:
#                 content = "Sorry, I couldn't generate a response."

#             conversation = self.chat_service.get_conversation(chat_response.conversation_id)
#             collection = self.chat_service.get_collection_by_name(
#                 self.test_user["sub"], 
#                 conversation.title
#             )
            
#             response_subject = collection.collection_name
#             if existing_collection and collection.id == existing_collection.id:
#                 response_subject = f"Re: {response_subject}"

#             return {
#                 "content": content,
#                 "subject": response_subject,
#                 "collection": collection,
#                 "is_reply": existing_collection and collection.id == existing_collection.id
#             }
            
#         except Exception as e:
#             logger.error(f"Error processing conversation: {str(e)}")
#             return None