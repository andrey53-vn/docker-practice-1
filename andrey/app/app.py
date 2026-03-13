from flask import Flask, request, jsonify
import sqlite3
import json
import os

app = Flask(__name__)
DB_PATH = "images.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            tags TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/images", methods=["POST"])
def create_image():
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    url = data.get("url")
    width = data.get("width")
    height = data.get("height")
    tags = data.get("tags")

    if not url or width is None or height is None or tags is None:
        return jsonify({"error": "Fields url, width, height, tags are required"}), 400

    if not isinstance(tags, list):
        return jsonify({"error": "tags must be a list"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO images (url, width, height, tags) VALUES (?, ?, ?, ?)",
        (url, width, height, json.dumps(tags))
    )
    image_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "id": image_id,
        "url": url,
        "width": width,
        "height": height,
        "tags": tags
    }), 201


@app.route("/images", methods=["GET"])
def get_images():
    tag = request.args.get("tag")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM images")
    rows = cursor.fetchall()
    conn.close()

    images = []
    for row in rows:
        image_tags = json.loads(row["tags"])
        image = {
            "id": row["id"],
            "url": row["url"],
            "width": row["width"],
            "height": row["height"],
            "tags": image_tags
        }

        if tag is None or tag in image_tags:
            images.append(image)

    return jsonify(images), 200


@app.route("/images/<int:image_id>", methods=["GET"])
def get_image(image_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM images WHERE id = ?", (image_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Image not found"}), 404

    image_tags = json.loads(row["tags"])
    image = {
        "id": row["id"],
        "url": row["url"],
        "width": row["width"],
        "height": row["height"],
        "tags": image_tags
    }

    return jsonify(image), 200


if __name__ == "__main__":
    init_db()  # Инициализируем БД при запуске
    app.run(debug=True, host="0.0.0.0", port=5000)