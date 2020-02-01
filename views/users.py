from mongoengine import ValidationError
from werkzeug.security import generate_password_hash

from app import app
from flask import jsonify, request
from models import Post, User
from views.authorization import login_required


# @app.route("/api/users/<string:username>")
# def user_username(username):
#     user = User.objects(username=username).first()
#     print(user)
#     if user:
#         return jsonify(user.to_public_json())
#     else:
#         return jsonify({"error": "User not found"}), 404


@app.route("/api/user_star")
@login_required
def user_star(userid):
    user = User.objects(id=userid).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    posts = Post.objects(user_collect=user)
    return jsonify(posts.to_public_json())


@app.route("/api/user_comments")
@login_required
def user_comments(userid):
    user = User.objects(id=userid).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    commentLst = []
    try:
        posts = Post.objects(comments__user=user)
        for post in posts:
            comments = post.comments
            for comment in comments:
                commentLst.append({
                    "content": comment.content,
                    "created": comment.created.strftime("%Y-%m-%d %H:%M:%S"),
                    "post": {
                        "title": post.title
                    }
                })
    except:
        print('error')

    return jsonify(commentLst)


@app.route("/api/user_follow/<string:uid>", methods=["GET"])
@login_required
def user_follow(userid, uid):
    if userid == uid:
        return jsonify('不能关注自己')
    try:
        userFollowed = User.objects(pk=uid).first()
    except ValidationError:
        return jsonify({"error": "User not found"}), 404

    user = User.objects(id=userid).first()

    user_followed = user.user_followed

    if userFollowed.username in [u["username"] for u in user_followed]:
        # User already agree
        user_collect_index = [d.username for d in user_followed].index(userFollowed.username)
        user_followed.pop(user_collect_index)
        user.save()
        return jsonify('取消关注成功')
    else:
        user_followed.append(userFollowed)
        user.save()
        return jsonify('关注成功')


@app.route("/api/user_follows", methods=["GET"])
@login_required
def user_follows(userid):
    user = User.objects(id=userid).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = {}
    try:
        user_followed = user.user_followed

        data = {

            "data": [{
                "id": str(user.id),
                "nickname": user.email,
                "head_img": user.head_img,
                "created": user.created.strftime("%Y-%m-%d %H:%M:%S"),
            } for user in user_followed],

        }
    except:
        print('error')

    return jsonify(data)


@app.route("/api/me", methods=["GET"])
@login_required
def get_user_info(userid):
    user = User.objects(id=userid).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_public_json())


@app.route("/api/user_update", methods=["POST"])
@login_required
def user_update(userid):
    body = request.json
    if not body:
        return jsonify({"error": "Data not specified"}), 409

    user = User.objects(id=userid).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if body.get("head_img"):
        user.head_img = body.get("head_img")
    if body.get("password"):
        user.password = generate_password_hash(body.get("password"))
    if body.get("username"):
        user.username = body.get("username")
    if body.get("gender") != None:
        user.gender = body.get("gender")

    user.save()
    return jsonify(user.to_public_json())
