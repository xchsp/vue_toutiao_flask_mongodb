from app import app
from flask import jsonify
from models import Category


@app.route("/api/category")
def category():
    # cate = Category(
    #     name='css',
    # ).save()

    category = Category.objects()

    return jsonify(category.to_public_json())


