from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

# MongoDB Atlas connection string
uri = "mongodb+srv://ayushrnj18:Spincricket%4018@cluster0.lsac64b.mongodb.net/"

# Connect to MongoDB Atlas
try:
    client = MongoClient(uri)
    db = client.library_system
    print("Connected to MongoDB Atlas successfully")
except Exception as e:
    print(f"Failed to connect to MongoDB Atlas: {e}")
    exit()

# Create collections if they don't exist
collections = db.list_collection_names()

if 'users' not in collections:
    db.create_collection('users')
    print("Created 'users' collection")
else:
    print("'users' collection already exists")

if 'documents' not in collections:
    db.create_collection('documents')
    print("Created 'documents' collection")
else:
    print("'documents' collection already exists")

# Create default admin user if it doesn't exist
admin_user = db.users.find_one({'name': 'admin'})
if not admin_user:
    db.users.insert_one({
        'name': 'admin',
        'password_hash': 'admin123',
        'role': 'admin',
        'created_at': datetime.now()
    })
    print("Created admin user: username=admin, password=admin123")
else:
    print("Admin user already exists")

# Upload PDFs from folder to documents collection
FOLDER_PATH = r"C:\Users\ayush\Documents\cc_library_system_rag\static\uploads"

if os.path.exists(FOLDER_PATH):
    pdf_files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.pdf')]
    
    if pdf_files:
        print(f"\nFound {len(pdf_files)} PDF files in uploads folder")
        
        for pdf_name in pdf_files:
            file_path = os.path.join(FOLDER_PATH, pdf_name)
            
            # Check if document already exists
            existing_doc = db.documents.find_one({'filename': pdf_name})
            if not existing_doc:
                with open(file_path, 'rb') as f:
                    doc = {
                        'filename': pdf_name,
                        'file_content': f.read(),
                        'file_size_kb': round(os.path.getsize(file_path) / 1024, 2),
                        'upload_date': datetime.now(),
                        'uploaded_by': 'admin'
                    }
                    db.documents.insert_one(doc)
                    print(f"   Uploaded: {pdf_name} ({doc['file_size_kb']} KB)")
            else:
                print(f"   Skipped (already exists): {pdf_name}")
    else:
        print("\nNo PDF files found in uploads folder")
else:
    print(f"\nUploads folder not found: {FOLDER_PATH}")

# List all users to verify
print("\nCurrent users in database:")
users = db.users.find()
for user in users:
    print(f"   Username: {user['name']}, Role: {user['role']}")

# Show document count
doc_count = db.documents.count_documents({})
print(f"\nTotal documents in collection: {doc_count}")

# List all documents
if doc_count > 0:
    print("\nDocuments in library:")
    docs = db.documents.find()
    for doc in docs:
        print(f"   {doc['filename']} - {doc.get('file_size_kb', 'N/A')} KB")

print("\nSetup complete!")