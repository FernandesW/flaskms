from src.constants.http_status_codes import (
    HTTP_400_BAD_REQUEST,
    HTTP_409_CONFLICT,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED,
    HTTP_202_ACCEPTED,
    HTTP_200_OK
)
from flask import Blueprint, jsonify, request, make_response
from flasgger import swag_from
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from src.database import User, db, ma, BookmarkSchema, UserSchema
from flask_jwt_extended import (
    jwt_required,
    create_access_token,
    create_refresh_token,
    get_jwt_identity
)
import json

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.route('/register', methods=["POST"])
@swag_from("./docs/auth/login.yaml")
def register():
    if request.json is None:
        return jsonify({"Error": "Username Not provided"})

    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if(len(password) < 6):
        return jsonify({"error": "Password too short"}), HTTP_400_BAD_REQUEST

    if(len(username) < 3):
        return jsonify({"error": "Username too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() < 3 or " " in username:
        return jsonify({"error": "Username should be alphanumeric or Remove spaces in username"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({"error": "Email not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({"error": "email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(username=username).first() is not None:
        return jsonify({"error": "Username is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)
    user = User(username=username, password=pwd_hash, email=email)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User Created",
        "user": {
            "username": username, "email": email
        }
    }), HTTP_201_CREATED


@auth.route("/login", methods=["POST"])
@swag_from("./docs/auth/login.yaml")
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    user = User.query.filter_by(email=email).first()

    if user:
        password_correct = check_password_hash(user.password, password)

        if password_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify(
                {
                    "refresh": refresh,
                    "access": access,
                    "username": user.username,
                    "email": user.email

                }
            ), HTTP_200_OK

    return jsonify({"Error": "Wrong Password"}), HTTP_401_UNAUTHORIZED


@auth.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    output = UserSchema().dump(user)
    return jsonify(output), HTTP_200_OK


@auth.route("/token/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh_user_token():
    identity=get_jwt_identity()
    access=create_access_token(identity=identity)
    return jsonify(
        {
            'access':access
        }
    )