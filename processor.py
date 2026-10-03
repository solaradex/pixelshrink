from PIL import Image
import io

def optimize_image(file, quality=80):
    data = file.read()
    original_size = len(data)

    img = Image.open(io.BytesIO(data))
    img = img.convert("RGB")

    output = io.BytesIO()
    img.save(output, format="WEBP", quality=quality, method=6)

    optimized_size = len(output.getvalue())
    savings = (1 - optimized_size / original_size) * 100

    return output.getvalue(), {
        "original": original_size,
        "optimized": optimized_size,
        "savings": round(savings, 2)
    }
