from mongoengine import ValidationError

from app import app
from flask import jsonify
from models import Post, User
from views.authorization import login_required


@app.route("/api/users/<string:username>")
def user_username(username):
    user = User.objects(username=username).first()
    print(user)
    if user:
        return jsonify(user.to_public_json())
    else:
        return jsonify({"error": "User not found"}), 404


@app.route("/api/user_star")
@login_required
def user_star(username):
    user = User.objects(username=username).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    posts = Post.objects(user_collect=user)
    return jsonify(posts.to_public_json())


@app.route("/api/user_comments")
@login_required
def user_comments(username):
    user = User.objects(username=username).first()
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
def user_follow(username, uid):
    try:
        userFollowed = User.objects(pk=uid).first()
    except ValidationError:
        return jsonify({"error": "User not found"}), 404

    user = User.objects(username=username).first()

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
def user_follows(username):
    user = User.objects(username=username).first()
    print(user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = {}
    try:
        user_followed = user.user_followed

        data = {

            "data": [{
                "id": str(user.id),
                "nickname": user.email
            } for user in user_followed],

        }
    except:
        print('error')

    return jsonify(data)
