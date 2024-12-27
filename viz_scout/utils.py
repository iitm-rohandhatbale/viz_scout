import io
import cv2
import numpy as np

from PIL import Image


class ImageLoader:
    @staticmethod
    def load(input_data):
        """
        Load an image from various formats into a NumPy array.
        """
        if isinstance(input_data, str):  # File path
            image = cv2.imread(input_data)
            if image is None:
                raise ValueError(f"Cannot load image from path: {input_data}")
        elif isinstance(input_data, np.ndarray):  # NumPy array
            image = input_data
        elif isinstance(input_data, bytes):  # Bytes
            pil_image = Image.open(io.BytesIO(input_data))
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        elif isinstance(input_data, io.BytesIO):
            pil_image = Image.open(input_data)
            image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        elif isinstance(input_data, Image.Image):
            image = cv2.cvtColor(np.array(input_data), cv2.COLOR_RGB2BGR)
        else:
            raise TypeError("Unsupported input type. Must be a file path, NumPy array, or bytes.")
        return image


def normalize_score(value, min_value, max_value):
    """
    Normalize a value to a score between 0 and 10.
    """
    if value <= min_value:
        return 0
    elif value >= max_value:
        return 10
    else:
        return float(10 * (value - min_value) / (max_value - min_value))
