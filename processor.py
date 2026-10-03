from PIL import Image, UnidentifiedImageError
import io

MAX_PIXELS = 25_000_000

def optimize_image(file, quality=80):
    data = file.read()
    original_size = len(data)

    if original_size == 0:
        raise ValueError("The uploaded file is empty.")

    try:
        with Image.open(io.BytesIO(data)) as img:
            if img.width * img.height > MAX_PIXELS:
                raise ValueError("Image exceeds the 25-megapixel limit.")

            img.verify()

        with Image.open(io.BytesIO(data)) as img:
            img = img.convert("RGB")

            output = io.BytesIO()
            img.save(output, format="WEBP", quality=quality, method=6)

    except (UnidentifiedImageError, OSError) as e:
        raise ValueError("Invalid or unsupported image file.") from e

    optimized_data = output.getvalue()
    optimized_size = len(optimized_data)

    savings = (1 - optimized_size / original_size) * 100

    return optimized_data, {
        "original": original_size,
        "optimized": optimized_size,
        "savings": round(savings, 2)
    }
