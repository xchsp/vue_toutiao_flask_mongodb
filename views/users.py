import time

import config
import os
import uuid

from app import app
from flask import jsonify, request
from models import Post, User, Comment, Subvue
from mongoengine.errors import ValidationError
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
