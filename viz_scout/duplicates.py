import numpy as np
import logging

from icecream import ic
from tqdm import tqdm
from PIL import Image
from imagededup.methods import DHash, CNN
from concurrent.futures import ThreadPoolExecutor
from .dataset import DatasetLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Logging initialized for duplicates")


class DuplicateDetector:
    def __init__(self, images=None, dataset_path=None, minio_config=None, s3_config=None):
        if not images and not dataset_path:
            raise ValueError("Either 'images (dict)' or 'dataset_path (string, s3 link, minio link)' must be provided.")

        if images:
            if not isinstance(images, dict):
                raise ValueError("Expected 'images' to be a dictionary loaded with dataloader object"
                                 "with image paths as keys and streams as values.")
            self.images: dict = images  # {image_path: image_stream}

        if dataset_path:
            self.images = DatasetLoader(source=dataset_path, s3_config=s3_config,
                                        minio_config=minio_config).load_images()
        ic(self.images)
        self.img_inc_dict = None
        self.exact_duplicates_dict = None
        logging.info(f"Duplicate Detector initialized with {len(self.images)} images.")

    def get_exact_duplicates(self) -> dict:
        """
        Find exact duplicates by comparing file hashes.
        """
        if self.exact_duplicates_dict is not None:
            return self.exact_duplicates_dict

        logging.info("Starting exact duplicate detection...")
        self.img_inc_dict = self._generate_img_enc()
        logging.info(f"Generated encodings for {len(self.img_inc_dict)} images.")

        hasher = CNN()
        raw_exact_duplicates_dict = hasher.find_duplicates(encoding_map=self.img_inc_dict,
                                                           min_similarity_threshold=1.0)

        self.exact_duplicates_dict = self._remove_symmetric_duplicates(raw_exact_duplicates_dict)
        logging.info("Exact duplicate detection completed.")

        return self.exact_duplicates_dict

    def get_near_duplicates(self) -> dict:
        """
        Find near duplicates using perceptual hashing.
        """
        try:
            logging.info("Starting near duplicate detection...")
            image_encoding_dict = self.img_inc_dict.copy()
            if self.exact_duplicates_dict is None:
                self.exact_duplicates_dict = self.get_exact_duplicates()
                image_encoding_dict = self.img_inc_dict.copy()

            for key_image, list_duplicates in tqdm(self.exact_duplicates_dict.items(),
                                                   desc="Removing exact duplicates"):
                for dup_image in list_duplicates:
                    del image_encoding_dict[dup_image]

            hasher = CNN()
            raw_near_duplicates_dict = hasher.find_duplicates(encoding_map=image_encoding_dict,
                                                              min_similarity_threshold=0.8)
            near_duplicates_dict = self._remove_symmetric_duplicates(raw_near_duplicates_dict)
            logging.info("Near duplicate detection completed.")
        except Exception as e:
            logging.error(f"Error finding near duplicates: {e}")
            raise

        return near_duplicates_dict

    @staticmethod
    def _remove_symmetric_duplicates(duplicates_dict: dict) -> dict:
        """
        Remove symmetric duplicates from the duplicates dictionary.
        :arg duplicates_dict: A dictionary containing the duplicates.
        :return: A dictionary with the symmetric duplicates removed.
        """
        filtered_duplicates = {}
        processed_images = set()
        try:
            for key_image, list_duplicates in duplicates_dict.items():
                if len(list_duplicates) > 0:
                    if key_image not in processed_images:
                        filtered_list_duplicates = [str(dup_img) for dup_img in list_duplicates if
                                                    dup_img not in processed_images]
                        filtered_duplicates[str(key_image)] = filtered_list_duplicates
                        processed_images.add(key_image)
                        processed_images.update(filtered_list_duplicates)
        except Exception as e:
            logging.error(f"Error removing symmetric duplicates: {e}")
            raise

        return filtered_duplicates

    def _generate_img_enc(self):
        """
        Generate image encodings for all images in the dataset.
        """
        num_images = len(self.images)
        image_encoding_dict = {}

        try:
            logging.info("Generating image encodings...")

            if num_images < 100:
                for img_meta in tqdm(self.images.items(), desc="Encoding images"):
                    image_path, image_encoding = self._compute_cnn_encoding(img_meta)
                    image_encoding_dict[image_path] = image_encoding
            else:
                with ThreadPoolExecutor(max_workers=4) as executor:
                    image_encoding_dict = dict(tqdm(executor.map(self._compute_cnn_encoding, self.images.items()),
                                                    total=num_images, desc="Encoding images in parallel"))
            logging.info("Image encoding generation completed.")
        except Exception as e:
            logging.error(f"Error generating image encodings: {e}")
            raise

        return image_encoding_dict

    @staticmethod
    def _compute_dhash_encoding(img_meta):
        """
        Compute hash for a file.
        """
        try:
            image_path, image_stream = img_meta
            image_array = np.asarray(Image.open(image_stream))
            dhash = DHash()
            return image_path, dhash.encode_image(image_array)
        except Exception as e:
            logging.error(f"Error computing dhash encoding: {e}")
            raise

    @staticmethod
    def _compute_cnn_encoding(img_meta):
        """
        Compute hash for a file.
        """
        try:
            image_path, image_stream = img_meta
            image_array = np.array(Image.open(image_stream))
            cnn_encoder = CNN()
            image_encoding = cnn_encoder.encode_image(image_array=image_array)[0]
            return image_path, image_encoding
        except Exception as e:
            logging.error(f"Error computing cnn encoding: {e}")
            raise
