import base64
import io
from PIL import Image
from typing import Tuple

def encode_image(image_path: str) -> Tuple[str, str]:
    """
    Encode an image file to base64 and determine its format.

    Args:
        image_path (str): The path to the image file.

    Returns:
        Tuple[str, str]: A tuple containing the base64 encoded image string and the image format.

    Raises:
        ValueError: If the image format is not supported (only PNG and JPEG are allowed).
    """
    if image_path.lower().endswith('.png'):
        image_format = "PNG"
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        image_format = "JPEG"
    else:
        raise ValueError("Unsupported image format. Only PNG and JPEG are allowed.")

    with Image.open(image_path) as img:
        buffer = io.BytesIO()
        img.save(buffer, format=image_format)
        encoded_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return encoded_image, image_format

def get_image_data_url(encoded_image: str, image_format: str) -> str:
    """
    Create a data URL for an encoded image.

    Args:
        encoded_image (str): The base64 encoded image string.
        image_format (str): The format of the image (e.g., "PNG" or "JPEG").

    Returns:
        str: A data URL for the image.
    """
    return f"data:image/{image_format.lower()};base64,{encoded_image}"
