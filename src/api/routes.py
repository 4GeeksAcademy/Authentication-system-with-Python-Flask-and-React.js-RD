from flask import request, jsonify, Blueprint
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from api.models import db, User  # using User only

api = Blueprint("api", __name__)
CORS(api)

# --- Sign up ---
@api.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}

    required = ["username", "email", "password"]
    for f in required:
        if not data.get(f) or not str(data[f]).strip():
            return jsonify({"error": f"{f} is required"}), 400

    username = data["username"].strip()
    email = data["email"].strip().lower()
    password = data["password"]

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password)
    )

    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "username or email already exists"}), 409

    return jsonify({"message": "User created successfully", "user": user.serialize()}), 201


# --- Login with email/password ---
@api.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"message": "login ok", "token": token, "user": user.serialize()}), 200


# --- Token with username/password (same as earlier) ---
@api.route("/token", methods=["POST"])
def create_token():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"msg": "username and password are required"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Bad username or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user_id": user.id, "username": user.username}), 200


# --- Current user (protected) ---
@api.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.serialize()), 200


# --- List users (optional utility) ---
@api.route("/users", methods=["GET"])
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return jsonify([u.serialize() for u in users]), 200


# --- Get one user by id (optional utility) ---
@api.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int):
    user = db.session.get(User, user_id)  # SQLAlchemy 2.x style
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200
