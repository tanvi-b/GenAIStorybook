#got API authentication code from https://huggingface.co/docs/api-inference/getting-started
#got code structure for images from here: https://huggingface.co/docs/api-inference/tasks/text-to-image

import os
import time
import requests
import io
from PIL import Image

TEXT_API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-Coder-32B-Instruct"
TEXT_API_BACKUP_URL = "https://api-inference.huggingface.co/models/NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO"
IMAGE_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3-medium-diffusers"
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
headers = {"Authorization": HF_API_KEY}

def fetch_text_response(payload):
    for api_url in [TEXT_API_URL, TEXT_API_BACKUP_URL]:
        while True:
            print("making story text" + api_url);
            response = requests.post(api_url, headers=headers, json=payload)
            print("after requests post");
            result = response.json()
            print ("result generated");

            if "error" in result:
                if "loading" in result["error"]:
                    print("Model is loading...")
                    time.sleep(20)
                    continue
                else:
                    print(f"Error: {result['error']}")
                    break

            print(result[0].get("generated_text", "").strip());
            return result[0].get("generated_text", "").strip()
    return None

def generate_image_for_page(page_text, page_num):
    images_directory = "images"
    image_response = requests.post(IMAGE_API_URL, headers=headers, json={"inputs": page_text})
    image_path = None
    if image_response.status_code == 200:
        try:
            image_bytes = image_response.content
            image = Image.open(io.BytesIO(image_bytes))
            image_path = os.path.join(images_directory, f"page_{page_num + 1}.png")
            image.save(image_path)
            print(f"Image saved at: {image_path}")
        except Exception as e:
            print(f"Couldn't process image for page {page_num + 1}: {e}")
    else:
        print(f"Couldn't create image for page {page_num + 1}. HTTP code: {image_response.status_code}")
    return image_path;

def generate_text(prompt, max_pages=5, tokens_per_page=100):
    story = prompt.strip()
    story_pages = []

    images_directory = "images"
    if os.path.exists(images_directory):
        for file in os.listdir(images_directory):
            file_path = os.path.join(images_directory, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        os.makedirs(images_directory)

    print("now preparing payload");
    for page_num in range(max_pages):
        payload = {
            "inputs": story,
            "parameters": {
                "max_new_tokens": tokens_per_page,
                "return_full_text": False,
                "temperature": 0.7
            }
        }
        print ("now calling fetch text response");

        page_text = fetch_text_response(payload)
        print(page_text);

        if not page_text:
            print("Story finished or error occurred.")
            break

        story += " " + page_text
        if (page_num==0):
            image_path = generate_image_for_page(page_text, page_num)
        else:
            image_path = None;

        story_pages.append({
            "text": page_text,
            "image": image_path if image_path else None
        })
    return story_pages