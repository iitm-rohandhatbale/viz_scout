import io
import numpy as np

from PIL import Image


class CorruptionDetector:
    def __init__(self):
        pass

    def is_corrupt(self, input_data):
        """
        Check if an image is corrupt.
        """
        try:
            if isinstance(input_data, str):  # File path
                Image.open(input_data).verify()
            elif isinstance(input_data, bytes):  # Bytes
                Image.open(io.BytesIO(input_data)).verify()
            elif isinstance(input_data, np.ndarray):  # NumPy array
                pil_image = Image.fromarray(input_data)
                pil_image.verify()
            elif isinstance(input_data, io.BytesIO):
                Image.open(input_data).verify()
            else:
                raise TypeError("Unsupported input type for corruption check.")
            return False
        except Exception:
            return True

    def get_corrupt_images(self, images):
        """
        Get a list of corrupt images.
        """
        return [img for img in images if self.is_corrupt(img)]
