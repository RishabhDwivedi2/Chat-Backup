# app/cloud/firebase_config.py

import os
from firebase_admin import credentials, initialize_app, storage
import logging
from google.auth import default
import google.auth.transport.requests

logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase Admin SDK with explicit ADC path for Windows"""
    try:
        # Check if already initialized
        try:
            return storage.bucket()
        except ValueError:
            pass
            
        # Set explicit path for ADC credentials
        adc_path = os.path.expanduser("~\\AppData\\Roaming\\gcloud\\application_default_credentials.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = adc_path
        
        logger.info(f"Using ADC credentials from: {adc_path}")
        
        # Verify credentials before initialization
        try:
            credentials_obj, project_id = default()
            # Force token refresh to verify credentials
            request = google.auth.transport.requests.Request()
            credentials_obj.refresh(request)
            logger.info("Successfully verified ADC credentials")
        except Exception as e:
            logger.error(f"Failed to verify credentials: {str(e)}")
            raise
            
        # Initialize Firebase
        initialize_app(options={
            'projectId': 'rchat-3afe7',
            'storageBucket': 'rchat-3afe7.firebasestorage.app'
        })
        
        bucket = storage.bucket()
        
        # Test bucket access
        try:
            bucket.exists()
            logger.info("Successfully verified bucket access")
        except Exception as e:
            logger.error(f"Failed to access bucket: {str(e)}")
            raise
            
        return bucket

    except Exception as e:
        logger.error(f"Firebase initialization failed: {str(e)}", exc_info=True)
        raise Exception(f"Firebase initialization error: {str(e)}")


# import firebase_admin
# from firebase_admin import credentials, storage
# import os
# from pathlib import Path

# def initialize_firebase():
#     """Initialize Firebase Admin SDK"""
#     try:
#         try:
#             firebase_admin.get_app()
#             return
#         except ValueError:
#             pass

#         cred = credentials.Certificate({
#             "type": "service_account",
#             "project_id": "rchat-3afe7",
#             "private_key_id": "YOUR_PRIVATE_KEY_ID",  
#             "private_key": "YOUR_PRIVATE_KEY",  
#             "client_email": "YOUR_CLIENT_EMAIL",  
#             "client_id": "YOUR_CLIENT_ID",  
#             "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#             "token_uri": "https://oauth2.googleapis.com/token",
#             "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#             "client_x509_cert_url": "YOUR_CERT_URL",  
#             "universe_domain": "googleapis.com"
#         })

#         firebase_admin.initialize_app(cred, {
#             'storageBucket': 'rchat-3afe7.firebasestorage.app'
#         })
        
#     except Exception as e:
#         print(f"Error initializing Firebase: {str(e)}")
#         raise




# rules_version = '2';
# service firebase.storage {
#   match /b/{bucket}/o {
#     // Rules for temporary folder
#     match /temp/{fileName} {
#       allow read: if true;  // Anyone can read temp files
#       allow write: if true;  // Anyone can write temp files
#       // Optional: Auto-delete files older than 24 hours
#       allow delete: if resource.timeCreated < timestamp.date(2024, 1, 1);
#     }
    
#     // Rules for permanent folder
#     match /permanent/{fileName} {
#       allow read: if true;   // Anyone can read permanent files
#       // Only allow write if file is being moved from temp
#       allow write: if request.auth != null 
#                    && request.resource.size < 5 * 1024 * 1024; // 5MB limit
#     }
    
#     // Deny access to all other paths
#     match /{allPaths=**} {
#       allow read, write: if false;
#     }
#   }
# }