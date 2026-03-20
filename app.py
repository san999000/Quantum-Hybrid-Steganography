import os
import uuid
import zipfile
from flask import Flask, render_template, request, send_file, redirect, url_for

from stego.qkey import quantum_random_bits
from stego.crypto import encrypt_message, decrypt_message
from stego.lsb import embed_text_in_image, extract_text_from_image


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/encode", methods=["POST"])
def encode():
    image = request.files.get("image")
    message = request.form.get("message", "").strip()

    if not image or image.filename == "" or message == "":
        return redirect(url_for("home"))

    # Save input image
    input_path = os.path.join(UPLOAD_FOLDER, "input.png")
    image.save(input_path)

    # Quantum key bits (8 bits per character)
    key_bits = quantum_random_bits(len(message) * 8)

    # Encrypt message (base64 output)
    encrypted_b64 = encrypt_message(message, key_bits)

    # Unique filenames
    unique_id = uuid.uuid4().hex[:8]
    stego_filename = f"stego_{unique_id}.png"
    key_filename = f"key_{unique_id}.txt"
    zip_filename = f"stego_package_{unique_id}.zip"

    stego_path = os.path.join(OUTPUT_FOLDER, stego_filename)
    key_path = os.path.join(OUTPUT_FOLDER, key_filename)
    zip_path = os.path.join(OUTPUT_FOLDER, zip_filename)

    # Embed encrypted data into image
    embed_text_in_image(input_path, encrypted_b64, stego_path)

    # Save key file
    with open(key_path, "w", encoding="utf-8") as f:
        f.write(key_bits)

    # Create ZIP containing both
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(stego_path, arcname=stego_filename)
        zf.write(key_path, arcname=key_filename)

    # Download ZIP
    return send_file(zip_path, as_attachment=True)


@app.route("/decode", methods=["POST"])
def decode():
    stego_image = request.files.get("stego_image")
    key_file = request.files.get("key_file")

    if not stego_image or not key_file:
        return redirect(url_for("home"))

    unique_id = uuid.uuid4().hex[:8]
    stego_path = os.path.join(UPLOAD_FOLDER, f"stego_{unique_id}.png")
    key_path = os.path.join(UPLOAD_FOLDER, f"key_{unique_id}.txt")

    stego_image.save(stego_path)
    key_file.save(key_path)

    with open(key_path, "r", encoding="utf-8") as f:
        key_bits = f.read().strip()

    encrypted_b64 = extract_text_from_image(stego_path)
    decoded_message = decrypt_message(encrypted_b64, key_bits)

    return render_template("index.html", decoded_message=decoded_message)


if __name__ == "__main__":
    app.run(debug=True)