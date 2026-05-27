from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from functools import wraps
from datetime import datetime
import os
import secrets
import random

from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
from authlib.integrations.flask_client import OAuth

from chatbot.document_loader import load_documents
from chatbot.chunking import chunk_text
from chatbot.vector import add_chunks_to_vector_db
from chatbot.rag_pipeline import run_rag_pipeline

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["library_system"]
users_col = db.users
documents_col = db.documents

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"}
)

DEPARTMENTS = ["Engineering", "Safety", "HR", "Operations", "Finance", "Legal", "IT"]
DOC_TYPES = ["Manual", "Report", "Policy", "Guideline", "Circular", "Notification", "Form"]


def normalize_doc(doc):
    doc["_id"] = str(doc["_id"])
    doc.setdefault("doc_id", doc.get("_id"))

    if not doc.get("title"):
        doc["title"] = doc.get("filename", "Untitled")

    if not doc.get("type"):
        doc["type"] = random.choice(DOC_TYPES)
    if not doc.get("department"):
        doc["department"] = random.choice(DEPARTMENTS)

    # is_digital — True if file_content exists in MongoDB (works on Render, no disk needed)
    doc["is_digital"] = bool(doc.get("file_content") or doc.get("is_digital", False))

    # file_path stores the _id so the view route can fetch from MongoDB
    doc["file_path"] = doc["_id"] if doc["is_digital"] else None

    if not doc.get("created_at"):
        doc["created_at"] = doc.get("upload_date")

    # Strip binary blob before passing to template
    doc.pop("file_content", None)

    return doc


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


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    nonce = secrets.token_urlsafe(16)
    session["oidc_nonce"] = nonce
    return google.authorize_redirect(
        url_for("auth_callback", _external=True),
        nonce=nonce
    )


@app.route("/auth/callback")
def auth_callback():
    token = google.authorize_access_token()
    nonce = session.pop("oidc_nonce", None)
    user_info = google.parse_id_token(token, nonce=nonce)

    email = user_info["email"]
    user = users_col.find_one({"email": email})

    if not user:
        users_col.insert_one({
            "email": email,
            "name": user_info.get("name"),
            "picture": user_info.get("picture"),
            "role": "user",
            "created_at": datetime.now()
        })
        role = "user"
    else:
        role = user.get("role", "user")

    session["user_email"] = email
    session["user_role"] = role
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/index")
@login_required
def index():
    return render_template("index.html")


@app.route("/search/title")
@login_required
def search_title():
    query_str = request.args.get("title", "").strip()

    mongo_query = {
        "$or": [
            {"title":    {"$regex": query_str, "$options": "i"}},
            {"filename": {"$regex": query_str, "$options": "i"}},
        ]
    } if query_str else {}

    results = [normalize_doc(d) for d in documents_col.find(mongo_query)]
    return render_template("search_results.html", results=results, query=query_str)


@app.route("/search/recent")
@login_required
def search_recent():
    results = [
        normalize_doc(d) for d in
        documents_col.find().sort("upload_date", -1).limit(10)
    ]
    return render_template("search_results.html", results=results, query="Recent")


@app.route("/upload/new", methods=["POST"])
@login_required
def upload_new():
    title      = request.form.get("title", "").strip()
    doc_type   = request.form.get("type", random.choice(DOC_TYPES))
    department = request.form.get("department", random.choice(DEPARTMENTS))
    document   = request.files.get("document")

    if not document or not title:
        return "Upload Failed: title and file are required.", 400

    filename  = secure_filename(document.filename)
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    document.save(save_path)

    # Read binary content to store in MongoDB (makes files available on Render)
    with open(save_path, "rb") as f:
        file_bytes = f.read()

    file_size_kb = round(os.path.getsize(save_path) / 1024, 2)

    documents_col.insert_one({
        "title":        title,
        "filename":     filename,
        "file_path":    filename,
        "file_content": file_bytes,
        "file_size_kb": file_size_kb,
        "type":         doc_type,
        "department":   department,
        "is_digital":   True,
        "uploaded_by":  session["user_email"],
        "created_at":   datetime.utcnow(),
    })

    for doc in load_documents():
        if doc["title"] == filename:
            chunks = chunk_text(doc["content"])
            add_chunks_to_vector_db(chunks, metadata={"title": title})
            print(f"Ingested: {title}")
            break

    return redirect(url_for("upload_manage"))


@app.route("/document/<doc_id>/view")
@login_required
def view_document(doc_id):
    doc = documents_col.find_one({"_id": ObjectId(doc_id)})
    if not doc or "file_content" not in doc:
        return "File not found", 404

    filename = doc.get("filename", "document")
    if filename.endswith(".pdf"):
        mimetype = "application/pdf"
    elif filename.endswith(".docx"):
        mimetype = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        mimetype = "application/octet-stream"

    return Response(
        doc["file_content"],
        mimetype=mimetype,
        headers={"Content-Disposition": f"inline; filename={filename}"}
    )


@app.route("/upload/manage")
@login_required
def upload_manage():
    documents = [
        normalize_doc(d) for d in
        documents_col.find({"uploaded_by": session["user_email"]})
    ]
    return render_template("manage_uploads.html", documents=documents)


@app.route("/admin/users")
@login_required
@admin_required
def admin_users():
    users = list(users_col.find())
    for u in users:
        u["_id"] = str(u["_id"])
    return render_template("admin_users.html", users=users)


@app.route("/chatbot/query", methods=["POST"])
@login_required
def chatbot_query():
    user_input = request.json.get("message")
    try:
        answer = run_rag_pipeline(user_input)
        return jsonify({"reply": answer})
    except Exception as e:
        print("RAG Error:", e)
        return jsonify({"reply": "Error generating response."})


@app.route("/debug/docs")
@login_required
def debug_docs():
    docs = list(documents_col.find())
    for d in docs:
        d["_id"] = str(d["_id"])
        d.pop("file_content", None)
    return jsonify(docs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)