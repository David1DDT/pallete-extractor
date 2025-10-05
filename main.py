from flask import Flask, render_template, request, redirect, flash
import numpy as np
from PIL import Image, ImageEnhance

app = Flask(__name__)
app.secret_key = "secret"


@app.route("/", methods=["GET", "POST"])
def index():
    palette = None
    if request.method == "POST":
        if "image" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["image"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file:
            image = Image.open(file).convert("RGB")
            image = image.resize((150, 150))

            # Optional effects
            reduce_brightness = request.form.get("reduce_brightness") == "on"
            reduce_gradient = request.form.get("reduce_gradient") == "on"

            if reduce_brightness:
                # use Pillow's enhancer for better tone preservation
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(0.9)  # slightly dimmer (not too dark)

            if reduce_gradient:
                # reduce color variation by quantization (like posterization)
                image = image.quantize(colors=32).convert("RGB")

            image = np.array(image)
            # Count pixel frequencies
            pixels = image.reshape(-1, 3)
            unique, counts = np.unique(pixels, axis=0, return_counts=True)
            sorted_idx = np.argsort(-counts)
            top_colors = unique[sorted_idx][: int(request.form.get("colour_count", 5))]

            palette_hex = ["#%02x%02x%02x" % tuple(color) for color in top_colors]
            return render_template("index.html", palette=palette_hex)

    return render_template("index.html", palette=None)


if __name__ == "__main__":
    app.run(debug=True)
