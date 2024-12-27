import cv2
import numpy as np
import logging
from .utils import ImageLoader, normalize_score


class ImageQualityAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def brightness_score(input_data, min_value=0, max_value=255):
        """
        Calculate the brightness score of an image based on the average pixel intensity. 0 score is dark, 10 is bright.
        :param input_data: image data. Can be image path, NumPy array, or bytes.
        :param min_value: min brightness value for normalization. default is 0.
        :param max_value: max brightness value for normalization. default is 255.
        :return: brightness score between 0 and 10.
        """
        try:
            image = ImageLoader.load(input_data)
            grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(grayscale)
            return normalize_score(brightness, min_value, max_value)
        except Exception as e:
            logging.error(f"Error calculating brightness score: {e}")
            raise

    def darkness_score(self, input_data, min_value=0, max_value=255):
        """
        Calculate the darkness score of an image based on the average pixel intensity. 0 score is bright, 10 is dark.
        :param input_data: image data. Can be image path, NumPy array, or bytes.
        :param min_value: min brightness value for normalization. default is 0.
        :param max_value: max brightness value for normalization. default is 255.
        :return: darkness score between 0 and 10.
        """
        try:
            return 10 - self.brightness_score(input_data, min_value, max_value)
        except Exception as e:
            logging.error(f"Error calculating darkness score: {e}")
            raise

    @staticmethod
    def blur_score(input_data, min_value=0, max_value=1000):
        """
        Calculate the blur score of an image based on Laplacian variance. 0 score is blurry, 10 is sharp.
        :param input_data: image data. Can be image path, NumPy array, or bytes.
        :param min_value: min blur variance value for normalization.
        :param max_value: max blur variance value for normalization.
        :return: blur score between 0 and 10.
        """
        try:
            image = ImageLoader.load(input_data)
            grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur_variance = cv2.Laplacian(grayscale, cv2.CV_64F).var()
            return normalize_score(blur_variance, min_value, max_value)
        except Exception as e:
            logging.error(f"Error calculating blur score: {e}")
            raise

    @staticmethod
    def uniformity_score(input_data, min_value=0, max_value=100):
        """
        Calculate the uniformity score of an image based on the variance of pixel intensities.
        :param input_data: image data. Can be image path, NumPy array, or bytes.
        :param min_value: min variance value for normalization.
        :param max_value: max variance value for normalization.
        :return: uniformity score between 0 and 10.
        """
        try:
            image = ImageLoader.load(input_data)
            grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            variance = np.var(grayscale)
            return normalize_score(variance, min_value, max_value)
        except Exception as e:
            logging.error(f"Error calculating uniformity score: {e}")
            raise

    @staticmethod
    def filter_images(images, score_function, threshold):
        try:
            logging.info(f"Filtering images with threshold: {threshold}...")
            return [img for img in images if score_function(img) > threshold]
        except Exception as e:
            logging.error(f"Error filtering images: {e}")
            raise

    def get_bright_images(self, images, threshold=8):
        return self.filter_images(images, self.brightness_score, threshold)

    def get_dark_images(self, images, threshold=3):
        return self.filter_images(images, self.darkness_score, threshold)

    def get_blurry_images(self, images, threshold=3):
        return self.filter_images(images, lambda img: 10 - self.blur_score(img), threshold)

    def get_uniform_images(self, images, threshold=3):
        return self.filter_images(images, self.uniformity_score, threshold)
