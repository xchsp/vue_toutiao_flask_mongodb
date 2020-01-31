import jwt

from flask import jsonify, request
from functools import wraps
from models import User
from werkzeug.security import generate_password_hash, check_password_hash


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "Authorization" in request.headers:
            # Check whether token was sent
            authorization_header = request.headers["Authorization"]

            # Check whether token is valid
            try:
                token = authorization_header.split(" ")[1]
                user = jwt.decode(token, app.config["SECRET_KEY"])
            except:
                return jsonify({"error": "you are not logged in"}), 401

            return f(userid=user["userid"], *args, **kwargs)
        else:
            return jsonify({"error": "you are not logged in"}), 401
    return wrap


from app import app


@app.route("/api/register", methods=["POST"])
def sign_up():
    if not request.json.get("username"):
        return jsonify({"error": "Username not specified"}), 409
    if not request.json.get("email"):
        return jsonify({"error": "Email not specified"}), 409
    if not request.json.get("password"):
        return jsonify({"error": "Password not specified"}), 409

    if User.objects(username=request.json.get("username")):
        return jsonify({"error": "Username not available"}), 409
    if User.objects(email=request.json.get("email")):
        return jsonify({"error": "There is already an account with your email address"}), 409

    # Hash password with sha256
    hashed_password = generate_password_hash(request.json.get("password"))

    new_user = User(
        username=request.json.get("username"),
        email=request.json.get("email"),
        password=hashed_password,
        head_img='',
        gender=1,
        user_followed=[]
    ).save()

    token = jwt.encode({
        "userid": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "password": new_user.password,
        "created": str(new_user.created)
    }, app.config["SECRET_KEY"])

    return jsonify({
        "success": True,
        "user": {
            "username": new_user.username,
            "email": new_user.email,
            "password": new_user.password,
            "created": str(new_user.created)
        },
        "token": token.decode("UTF-8")
    })


@app.route("/api/login", methods=["POST"])
def login():
    if not request.json.get("username"):
        return jsonify({"error": "Username not specified"}), 409
    if not request.json.get("password"):
        return jsonify({"error": "Password not specified"}), 409

    try:
        username = request.json.get("username")
        print(username)
        users = User.objects(username=username)
    except:
        print('error')

    user = users.first()

    if user == None:
        return jsonify({"error": "User not found"}), 403



    if not check_password_hash(user.password, request.json.get("password")):
        return jsonify({"error": "Invalid password"}), 401

    token = jwt.encode({
        "userid": user.id,
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "created": str(user.created)
    }, app.config["SECRET_KEY"])

    return jsonify({
        # "success": True,
        "message": '登录成功',
        "data": {
            "user": user.username,
            "token": token.decode("UTF-8"),
            # "email": user.email,
            # "password": user.password,
            # "created": str(user.created)
        },

    })


@app.route("/api/login_c", methods=["POST"])
def login_c():
    if not request.json.get("username"):
        return jsonify({"error": "Username not specified"}), 409
    if not request.json.get("password"):
        return jsonify({"error": "Password not specified"}), 409

    try:
        username = request.json.get("username")
        print(username)
        users = User.objects(username=username)
    except:
        print('error')

    user = users.first()

    if user == None:
        return jsonify({"error": "User not found"}), 403



    if not check_password_hash(user.password, request.json.get("password")):
        return jsonify({"error": "Invalid password"}), 401

    token = jwt.encode({
        "userid": str(user.id),
        "username": user.username,
        "email": user.email,
        "password": user.password,
        "created": str(user.created)
    }, app.config["SECRET_KEY"])

    return jsonify({
        # "success": True,
        "statusCode": 200,
        "data": {
            "user": {'id':user.username},
            "token": token.decode("UTF-8"),
            # "email": user.email,
            # "password": user.password,
            # "created": str(user.created)
        },

    })