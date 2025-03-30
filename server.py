from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from Story_Generation.story_generation import generate_text, generate_image_for_page
import os
import time

app = Flask("AI Storybook")
CORS(app)

@app.route("/")
def render_index_page():
    return render_template('index.html')

@app.route("/generate", methods=["GET"])
def generate_story():
    story_prompt = request.args.get('story_idea')
    story_genre = request.args.get('genre')

    if not story_prompt:
        return jsonify({"error": "No story prompt given"}), 400
    if not story_genre:
        return jsonify({"error": "No story genre given"}), 400

    print("story prompt: " + story_prompt);
    story_pages = generate_text(
        story_prompt + " Write a short " + story_genre + " story. It should have a beginning, middle, and end. Conclude the story within "
                       "1000 words. It should be minimum 750 words and maximum 1000 words. Start printing story "
                       "immediately, don't include your own stuff like a title and other info. Begin story with "
                       "interesting hook. End the story with The End. Keep it a short concise story. The story should not be too long. "
                       "Don't start the story with a period. Write a short story. Start the story immediately with the word once."
    )

    formatted_pages = [
        {
            "text": page["text"],
            "image": f"/images/{os.path.basename(page['image'])}?timestamp={int(time.time())}" if page["image"] else None
        }
        for page in story_pages
    ]
    return jsonify(formatted_pages)

@app.route("/generate_image", methods=["POST"])
def generate_image():
    data = request.json
    if not data or "page_text" not in data or "page_num" not in data:
        return jsonify({"error": "Missing required parameters"}), 400

    page_text = data["page_text"]
    page_num = data["page_num"]

    image_path = generate_image_for_page(page_text, page_num)

    if image_path:
        return jsonify({
            "image_path": f"/images/{os.path.basename(image_path)}?timestamp={int(time.time())}"
        })
    else:
        return jsonify({"error": "Failed to generate image"}), 500

@app.route("/images/<path:filename>")
def give_image(filename):
    return send_from_directory("images", filename)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8080)