from pymongo import MongoClient
from bson.objectid import ObjectId

# Connect to MongoDB
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client.library
    print("Connected to MongoDB successfully")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    exit()

# Create collections if they don't exist
collections = db.list_collection_names()
if 'users' not in collections:
    db.create_collection('users')
    print("Created 'users' collection")
if 'documents' not in collections:
    db.create_collection('documents')
    print("Created 'documents' collection")

# Create default admin user if it doesn't exist
admin_user = db.users.find_one({'name': 'admin'})
if not admin_user:
    db.users.insert_one({
        'name': 'admin',
        'password_hash': 'admin123',
        'role': 'admin'
    })
    print("Created admin user: username=admin, password=admin123")
else:
    print("Admin user already exists")

# List all users to verify
print("\nCurrent users in database:")
users = db.users.find()
for user in users:
    print(f"Username: {user['name']}, Role: {user['role']}")