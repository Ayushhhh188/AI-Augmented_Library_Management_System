from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from functools import wraps
from datetime import datetime
import os
import secrets

from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from pymongo import MongoClient

from authlib.integrations.flask_client import OAuth

# -------------------------------
# Chatbot Modules
# -------------------------------
from chatbot.document_loader import extract_text
from chatbot.chunking import chunk_documents
from chatbot.vector import add_to_vector_db
from chatbot.rag_pipeline import ask_rag

# -------------------------------
# App Config
# -------------------------------
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

# -------------------------------
# MongoDB Atlas
# -------------------------------
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["library_system"]

users_col = db.users
documents_col = db.documents

# -------------------------------
# Upload Folder
# -------------------------------
UPLOAD_FOLDER = "static/uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# -------------------------------
# Google OAuth
# -------------------------------
oauth = OAuth(app)

google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile"
    }
)

# -------------------------------
# Decorators
# -------------------------------
def login_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        if "user_email" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated


def admin_required(f):

    @wraps(f)

    def decorated(*args, **kwargs):

        if session.get("user_role") != "admin":
            return "Access Denied", 403

        return f(*args, **kwargs)

    return decorated

# -------------------------------
# Home
# -------------------------------
@app.route("/")
def home():

    return render_template("home.html")

# -------------------------------
# Login
# -------------------------------
@app.route("/login")
def login():

    nonce = secrets.token_urlsafe(16)

    session["oidc_nonce"] = nonce

    return google.authorize_redirect(
        url_for("auth_callback", _external=True),
        nonce=nonce
    )

# -------------------------------
# Google Callback
# -------------------------------
@app.route("/auth/callback")
def auth_callback():

    token = google.authorize_access_token()

    nonce = session.pop("oidc_nonce", None)

    user_info = google.parse_id_token(
        token,
        nonce=nonce
    )

    email = user_info["email"]

    name = user_info.get("name")

    picture = user_info.get("picture")

    user = users_col.find_one({
        "email": email
    })

    if not user:

        users_col.insert_one({
            "email": email,
            "name": name,
            "picture": picture,
            "role": "user",
            "created_at": datetime.now()
        })

        role = "user"

    else:

        role = user.get("role", "user")

    session["user_email"] = email
    session["user_role"] = role

    return redirect(url_for("index"))

# -------------------------------
# Logout
# -------------------------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

# -------------------------------
# Main Library Page
# -------------------------------
@app.route("/index")
@login_required
def index():

    return render_template("index.html")

# -------------------------------
# Search By Title
# -------------------------------
@app.route("/search/title")
@login_required
def search_title():

    title = request.args.get("title", "")

    results = list(documents_col.find({
        "title": {
            "$regex": title,
            "$options": "i"
        }
    }))

    return render_template(
        "search_results.html",
        results=results,
        query=title
    )

# -------------------------------
# Recent Documents
# -------------------------------
@app.route("/search/recent")
@login_required
def search_recent():

    results = list(
        documents_col.find()
        .sort("created_at", -1)
        .limit(10)
    )

    return render_template(
        "search_results.html",
        results=results,
        query="Recent"
    )

# -------------------------------
# Upload New Document
# -------------------------------
@app.route("/upload/new", methods=["POST"])
@login_required
def upload_new():

    title = request.form.get("title")

    document = request.files.get("document")

    if document and title:

        filename = secure_filename(
            document.filename
        )

        save_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        # Save uploaded file
        document.save(save_path)

        # Save metadata to MongoDB
        documents_col.insert_one({
            "title": title,
            "uploaded_by": session["user_email"],
            "created_at": datetime.now(),
            "file_path": filename
        })

        # -------------------------------
        # RAG INGESTION PIPELINE
        # -------------------------------
        pages = extract_text(save_path)
        text = extract_text(save_path)

        chunked_documents = chunk_documents(
            pages
        )

        add_to_vector_db(
            chunked_documents
        )

        return redirect(
            url_for("upload_manage")
        )

    return "Upload Failed", 400

# -------------------------------
# Manage Uploads
# -------------------------------
@app.route("/upload/manage")
@login_required
def upload_manage():

    documents = list(documents_col.find({
        "uploaded_by": session["user_email"]
    }))

    return render_template(
        "manage_uploads.html",
        documents=documents
    )

# -------------------------------
# Admin Users
# -------------------------------
@app.route("/admin/users")
@login_required
@admin_required
def admin_users():

    users = list(users_col.find())

    return render_template(
        "admin_users.html",
        users=users
    )

# -------------------------------
# Chatbot Route
# -------------------------------
@app.route("/chatbot/query", methods=["POST"])
@login_required
def chatbot_query():

    user_input = request.json.get("message")

    try:

        answer = ask_rag(user_input)

        return jsonify({
            "reply": answer
        })

    except Exception as e:

        print("RAG Error:", e)

        return jsonify({
            "reply": "Error generating response."
        })

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":

    app.run(debug=True)