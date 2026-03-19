import os
import shutil
from typing import List, Dict

def write_comic_html(image_gallery: List[Dict[str, str]], comic_script: str) -> str:
    """
    Writes the final HTML file for the comic and copies image assets.
    """
    output_dir = "output"
    images_output_dir = os.path.join(output_dir, "images")

    # Create output directories if they don't exist
    if not os.path.exists(images_output_dir):
        os.makedirs(images_output_dir)

    # --- Image Copying Logic ---
    source_images_dir = "images"
    if os.path.exists(source_images_dir):
        expected_images = {os.path.basename(item.get("image_url", "")) for item in image_gallery if item.get("image_url")}

        for image_file in expected_images:
            source_path = os.path.join(source_images_dir, image_file)
            destination_path = os.path.join(images_output_dir, image_file)
            if os.path.exists(source_path):
                shutil.copy2(source_path, destination_path)
        print(f"Copied images from '{source_images_dir}' to '{images_output_dir}'")
    else:
        print(f"Warning: Source images directory '{source_images_dir}' not found.")


    # --- HTML Generation Logic ---
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ADK Comic</title>
    <style>
        body {{ font-family: sans-serif; margin: 0; background-color: #1a1a1a; color: #f0f0f0; }}
        .container {{ max-width: 800px; margin: 20px auto; padding: 0 20px; }}
        h1 {{ text-align: center; color: #fff; }}
        .panel {{ margin-bottom: 40px; border: 1px solid #444; border-radius: 8px; overflow: hidden; background-color: #2a2a2a;}}
        .panel img {{ display: block; width: 100%; height: auto; }}
        .panel .description {{ padding: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>My ADK Comic</h1>
        <div id="comic-strip">
'''

    sorted_gallery = sorted(image_gallery, key=lambda x: int(x.get('panel_number', 0)))
    panel_texts = [p.strip() for p in comic_script.split('---')]

    for i, item in enumerate(sorted_gallery):
        panel_num = item.get("panel_number")
        image_path = item.get("image_url")
        relative_image_path = os.path.join("images", os.path.basename(image_path)) if image_path and image_path != "error" else ""
        description = panel_texts[i] if i < len(panel_texts) else f"Description for panel {panel_num} is missing."

        html_content += f'''
            <div class="panel" id="panel-{panel_num}">
                <img src="{relative_image_path}" alt="Comic Panel {panel_num}">
                <div class="description">
                    <p>{description}</p>
                </div>
            </div>
'''

    html_content += '''
        </div>
    </div>
</body>
</html>
'''

    output_file_path = os.path.join(output_dir, "comic.html")
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return f"Successfully created your comic! You can find it at: {os.path.abspath(output_file_path)}"
    except IOError as e:
        return f"Error writing HTML file: {e}"
