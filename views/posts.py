import config
import os
import uuid

from app import app
from flask import jsonify, request
from models import Post, User, Comment, Subvue, Category, Cover
from mongoengine.errors import ValidationError
from views.authorization import login_required

# 后台请求
@app.route("/api/post_search", methods=["GET"])
@login_required
def post_search(username):
    try:
        user = User.objects(username=username).first()
    except ValidationError:
        return jsonify({"error": "User not found"}), 404

    keyword = request.args.get("keyword")

    from mongoengine.queryset.visitor import Q
    posts = Post.objects(Q(content__icontains=keyword)|Q(title__icontains=keyword))

    return jsonify(posts.to_public_json())

# 后台请求
@app.route("/api/post", methods=["GET"])
@login_required
def admin_get_posts(username):
    try:
        user = User.objects(username=username).first()
    except ValidationError:
        return jsonify({"error": "User not found"}), 404


    pageIndex = int(request.args.get("pageIndex"))
    pageSize = int(request.args.get("pageSize"))

    posts = Post.objects(user=user).order_by("-created")

    paginated_posts = posts.skip((pageIndex - 1) * pageSize).limit(pageSize)

    result = paginated_posts.to_public_json()

    res = {
        'total': posts.count(),
        'data': result
    }




    return jsonify(res)

# 前台请求
@app.route("/api/posts", methods=["GET"])
def client_get_posts():

    pageIndex = int(request.args.get("pageIndex"))
    pageSize = int(request.args.get("pageSize"))
    category = request.args.get("category")

    if category:
        posts = Post.objects(categories=category).order_by("-created")

    paginated_posts = posts.skip((pageIndex-1)*pageSize).limit(pageSize)

    return jsonify(paginated_posts.to_public_json())


@app.route("/api/posts", methods=["POST"])
@login_required
def posts_create(username):
    body = request.json
    if not body:
        return jsonify({"error": "Data not specified"}), 409
    if not body.get("title"):
        return jsonify({"error": "Title not specified"}), 409
    # if not request.form.get("subvue"):
    #     return jsonify({"error": "Subvue not specified"}), 409
    if not body.get("content"):
        return jsonify({"error": "Content not specified"}), 409

    # subvue = Subvue.objects(permalink__iexact=request.form.get("subvue")).first()
    # if not subvue:
    #     return jsonify({"error": "Subvue " + request.form.get("subvue") + " not found"}), 404

    user = User.objects(username=username).first()

    coverLst = []
    for cover in body.get('cover'):
        coverLst.append(cover['id'])

    post = Post(
        title=body.get("title"),
        categories=body.get('categories'),
        content=body.get("content"),
        user=user,
        covers=coverLst,
        type=body.get('type'),
        comments=[],
        user_collect=[],
        user_agree=[],
    ).save()

    return jsonify(post.to_public_json())

@app.route("/api/post_update/<string:id>", methods=["POST"])
@login_required
def posts_update(username,id):
    body = request.json
    if not body:
        return jsonify({"error": "Data not specified"}), 409
    if not body.get("title"):
        return jsonify({"error": "Title not specified"}), 409
    # if not request.form.get("subvue"):
    #     return jsonify({"error": "Subvue not specified"}), 409
    if not body.get("content"):
        return jsonify({"error": "Content not specified"}), 409

    # subvue = Subvue.objects(permalink__iexact=request.form.get("subvue")).first()
    # if not subvue:
    #     return jsonify({"error": "Subvue " + request.form.get("subvue") + " not found"}), 404

    user = User.objects(username=username).first()



    # post = Post(
    #     title=body.get("title"),
    #     categories=body.get('categories'),
    #     content=body.get("content"),
    #     user=user,
    #     covers=coverLst,
    #     type=body.get('type')
    #     # comments=[],
    # ).save()
    try:
        post = Post.objects(pk=id).first()

        # If post has alreay been deleted
        if not post:
            raise ValidationError

        coverLst = post.covers
        coverLst.clear()
        for cover_obj in body.get('cover'):
            cover = Cover.objects(pk=cover_obj['id']).first()
            coverLst.append(cover)

        categoriesLst = post.categories
        categoriesLst.clear()
        for cid in body.get('categories'):
            category = Category.objects(pk=cid).first()
            categoriesLst.append(category)




        post.title=body.get("title")
        # post.categories=body.get('categories')
        post.content=body.get("content")
        # post.user=user
        # post.covers=coverLst
        post.type=body.get('type')
        post.save()

    except ValidationError:
        return jsonify({"error": "Post not found"}), 404

    return jsonify(post.to_public_json())

@app.route("/api/post/<string:id>")
@login_required
def posts_detail(username,id):
    try:
        post = Post.objects(pk=id).first()

        # If post has alreay been deleted
        if not post:
            raise ValidationError
    except ValidationError:
        return jsonify({"error": "Post not found"}), 404

    user_collect = post.user_collect

    if username in [u["username"] for u in user_collect]:
        post.has_star = True
    else:
        post.has_star = False

    user_agree = post.user_agree

    if username in [u["username"] for u in user_agree]:
        post.has_like = True
    else:
        post.has_like = False

    return jsonify(post.to_public_json())


# @app.route("/api/posts/user/<string:username>")
# def posts_user(username):
#     try:
#         user = User.objects(username=username).first()
#     except ValidationError:
#         return jsonify({"error": "User not found"}), 404
#
#     posts = Post.objects(user=user).order_by("-created")
#
#     return jsonify(posts.to_public_json())


@app.route("/api/posts/id/<string:id>", methods=["DELETE"])
@login_required
def posts_delete(username, id):
    try:
        post = Post.objects(pk=id).first()

        # If post has alreay been deleted
        if not post:
            raise ValidationError
    except ValidationError:
        return jsonify({"error": "Post not found"}), 404

    # Check whether action was called by creator of the post
    if username != post.user.username:
        return jsonify({"error": "You are not the creator of the post"}), 401

    post_info = post.to_public_json()

    post.delete()

    return jsonify(post_info)


@app.route("/api/post_comment/<string:id>", methods=["GET","POST"])
@login_required
def posts_create_comment(username, id):
    if request.method == 'POST':
        if not request.json.get('content'):
            return jsonify({"error": "No content specified"}), 409
        content = request.json.get('content')

        try:
            post = Post.objects(pk=id).first()
        except ValidationError:
            return jsonify({"error": "Post not found"}), 404

        user = User.objects(username=username).first()
        comments = post.comments
        comments.append(Comment(user=user, content=content))
        post.save()

        return jsonify([{
            "content": comment.content,
            "created": comment.created.strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                "id": str(comment.user.id),
                "username": comment.user.username
            }
        } for comment in post.comments][::-1]
        )
    else:
        try:
            post = Post.objects(pk=id).first()
        except ValidationError:
            return jsonify({"error": "Post not found"}), 404

        if not request.args.get('pageSize'):
            pageSize = len(post.comments)
        else:
            pageSize = int(request.args.get('pageSize'))


        commentLst = []
        for comment in post.comments[::-1]:
            commentLst.append({
            "content": comment.content,
            "created": comment.created.strftime("%Y-%m-%d %H:%M:%S"),
            "user": {
                "id": str(comment.user.id),
                "nickname": comment.user.username
            }
        })

            pageSize -= 1
            if pageSize == 0:
                break

        return jsonify(commentLst)

@app.route("/api/post_star/<string:id>", methods=["GET"])
@login_required
def post_star(username, id):
    try:
        post = Post.objects(pk=id).first()
    except ValidationError:
        return jsonify({"error": "Post not found"}), 404

    user = User.objects(username=username).first()

    user_collect = post.user_collect


    if username in [u["username"] for u in user_collect]:
        # User already collect
        user_collect_index = [d.username for d in user_collect].index(username)
        user_collect.pop(user_collect_index)
        post.save()
        return jsonify('取消成功')
    else:
        user_collect.append(user)
        post.save()
        return jsonify('收藏成功')

@app.route("/api/post_like/<string:id>", methods=["GET"])
@login_required
def post_like(username, id):
    try:
        post = Post.objects(pk=id).first()
    except ValidationError:
        return jsonify({"error": "Post not found"}), 404

    user = User.objects(username=username).first()

    user_agree = post.user_agree


    if username in [u["username"] for u in user_agree]:
        # User already agree
        user_collect_index = [d.username for d in user_agree].index(username)
        user_agree.pop(user_collect_index)
        post.save()
        return jsonify('取消成功')
    else:
        user_agree.append(user)
        post.save()
        return jsonify('点赞成功')





@app.route("/api/posts/<string:id>/downvote", methods=["POST"])
@login_required
def posts_downvote(username, id):
    try:
        post = Post.objects(pk=id).first()
    except ValidationError:
        return jsonify({"error": "Post not found"}), 404

    user = User.objects(username=username).first()

    upvotes = post.upvotes
    downvotes = post.downvotes

    if username in [u["username"] for u in downvotes]:
        # User already upvotes
        downvote_index = [d.username for d in downvotes].index(username)
        downvotes.pop(downvote_index)
    elif username in [u["username"] for u in upvotes]:
        upvote_index = [d.username for d in upvotes].index(username)
        upvotes.pop(upvote_index)
        downvotes.append(user)
    else:
        downvotes.append(user)

    post.save()

    return jsonify({
        "upvotes": post.to_public_json()["upvotes"],
        "downvotes": post.to_public_json()["downvotes"]
    })
