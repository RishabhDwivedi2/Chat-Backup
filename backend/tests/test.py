import firebase_admin
from firebase_admin import storage

firebase_admin.initialize_app(options={
    'projectId': 'rchat-3afe7',
    'storageBucket': 'rchat-3afe7.firebasestorage.app'
})

# Test storage access
bucket = storage.bucket()
print("Successfully connected to Firebase!")