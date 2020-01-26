import config
from app import app
from flask import jsonify, request
import os
import uuid

# from models import Category
from models import Cover


@app.route("/api/upload/", methods=["POST"])
def upload():
    image = request.files.get("file")
    if image:
        if not image.filename.endswith(tuple([".jpg", ".png"])):
            return jsonify({"error": "Image is not valid"}), 409

        # Generate random filename
        filename = str(uuid.uuid4()).replace("-", "") + "." + image.filename.split(".")[-1]
        image.save(os.path.join(config.image_upload_folder, filename))
        cover = Cover(
            url=filename,
        ).save()
    else:
        filename = None

    return jsonify(cover.to_public_json())


