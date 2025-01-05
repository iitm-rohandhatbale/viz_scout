import os
import json
import logging
import pandas as pd
from tqdm import tqdm
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from .corruption import CorruptionDetector
from .quality import ImageQualityAnalyzer
from .dataset import DatasetLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class EDAReport:
    def __init__(self, dataset_path, minio_config=None, s3_config=None, duplicate_check=False, blur_threshold=3,
                 batch_size=100, num_workers=4):
        """
        Initialize the EDA Report Generator with optimizations for large datasets.


        Args:
            dataset_path (str): Path to the dataset, can be local or S3/MinIO URI.
            minio_config (dict): MinIO configuration with keys: endpoint, access_key, secret_key.
            s3_config (dict): S3 configuration with keys: bucket, access_key, secret_key, region.
            duplicate_check (bool): Whether to check for duplicate images.
            blur_threshold (int): Threshold to classify blur score.
            batch_size (int): Number of images to process in each batch.
            num_workers (int): Number of parallel workers (threads) to process images concurrently.
        """
        self.dataset_path = dataset_path
        self.minio_config = minio_config
        self.s3_config = s3_config
        self.duplicate_check = duplicate_check
        self.blur_threshold = blur_threshold
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.data_df = None

        # Load the dataset
        logging.info(f"Loading dataset from {self.dataset_path}...")
        self.loader = DatasetLoader(dataset_path, minio_config, s3_config)
        self.images: dict = self.loader.load_images()
        logging.info(f"Loaded {len(self.images)} images.")

        # Initialize necessary detectors
        self.quality_analyzer = ImageQualityAnalyzer()
        self.corruption_detector = CorruptionDetector()

    def generate_report(self):
        """
        Generate the full EDA report with both dataset-level and image-level statistics using parallel processing.


        Returns:
            dict: A dictionary containing dataset and image-level statistics.
        """
        logging.info("Generating dataset-level statistics...")
        # Dataset-level statistics
        dataset_stats = self._get_dataset_stats()
        image_stats = []

        if len(self.images) < 1000:
            logging.info("Processing image-level statistics sequentially...")
            # Image-level statistics with sequential processing
            image_stats = self._get_image_stats()
        else:
            logging.info("Processing image-level statistics in parallel...")
            # Image-level statistics with parallel processing
            image_stats = self._get_image_stats_parallel()

        report = {
            "dataset_stats": dataset_stats,
            "image_stats": image_stats
        }
        
        self.data_df = pd.DataFrame(image_stats)
        logging.info("EDA report generation completed.")
        
        return report

    def _get_dataset_stats(self):
        """
        Get the overall statistics of the dataset.


        Returns:
            dict: Dataset-level statistics.
        """
        num_images = len(self.images)
        file_formats = set()
        corrupt_images = 0

        # Loop through images and gather stats
        for img_meta in self.images.items():
            img_path, img_stream = img_meta
            try:
                # Image format
                img_format = os.path.basename(img_path).split('.')[-1]
                file_formats.add(img_format)

                # # Check if the image is corrupt
                if self.corruption_detector.is_corrupt(img_stream):
                    corrupt_images += 1

            except Exception as e:
                logging.error(f"Error processing image {img_path}: {str(e)}")

        # Check for duplicate images
        exact_duplicate_images, near_duplicate_images = None, None
        if self.duplicate_check is True:
            from .duplicates import DuplicateDetector
            duplicate_detector = DuplicateDetector(images=self.images)
            exact_duplicate_images = duplicate_detector.get_exact_duplicates()
            near_duplicate_images = duplicate_detector.get_near_duplicates()

        return {
            "num_images": num_images,
            "file_formats": list(file_formats),
            "corrupt_images": corrupt_images,
            "exact_duplicate_images": exact_duplicate_images,
            "near_duplicate_images": near_duplicate_images
        }

    def _get_image_stats(self):
        """
        Get the statistics for each image sequentially.


        Returns:
            list: A list of dictionaries with image-level statistics.
        """
        image_stats = []
        for img_meta in tqdm(self.images.items(), desc="Processing Images Sequentially"):
            image_stats.append(self._process_image(img_meta))
        return image_stats

    def _get_image_stats_parallel(self):
        """
        Get the statistics for each image in parallel.


        Returns:
            list: A list of dictionaries with image-level statistics.
        """
        image_stats = []
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            list_img_meta = list(self.images.items())
            # Process in batches
            for batch_start in tqdm(range(0, len(list_img_meta), self.batch_size),
                                    desc="Processing Images in Parallel"):
                batch_end = min(batch_start + self.batch_size, len(list_img_meta))
                batch_img_meta = list_img_meta[batch_start:batch_end]

                # Map the batch of images to the executor for parallel processing
                batch_results = executor.map(self._process_image, batch_img_meta)

                # Collect results from batch
                image_stats.extend(batch_results)

        return image_stats

    def _process_image(self, img_meta):
        """
        Process an individual image to compute its stats.
        Args:
            img_meta(tuple): A tuple containing image path and image stream.
        Returns:
            dict: Image-level statistics.
        """

        img_path, img_stream = img_meta
        width = "NA"
        height = "NA"
        brightness = "NA"
        blur = "NA"
        uniformity = "NA"
        blur_classification = "NA"
        file_size = "NA"

        try:
            # Check for corruption
            corrupt = self.corruption_detector.is_corrupt(img_stream)

            if not corrupt:
                pil_image = Image.open(img_stream)
                width, height = pil_image.size

                # Calculate brightness, blur, and uniformity scores
                brightness = self.quality_analyzer.brightness_score(img_stream)
                blur = self.quality_analyzer.blur_score(img_stream)
                uniformity = self.quality_analyzer.uniformity_score(img_stream)

                # Classify image as blurry or clear based on the threshold
                blur_classification = "Blurry" if blur < self.blur_threshold else "Clear"

                # find file size
                file_size = img_stream.getbuffer().nbytes / 1024  # KB

            return {
                "filename": img_path,
                "file_size": file_size,
                "img_width": width,
                "img_height": height,
                "brightness_score": brightness,
                "blur_score": blur,
                "uniformity_score": uniformity,
                "blur_classification": blur_classification,
                "is_corrupt": corrupt
            }
        except Exception as e:
            return {
                "filename": img_path,
                "error": str(e)
            }

    @staticmethod
    def save_report(report, output_path="eda_report.json"):
        """
        Save the generated report to a JSON file.


        Args:
            report (dict): The EDA report dictionary.
            output_path (str): Path to save the report file.
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=4)
            logging.info(f"Report saved to {output_path}")
        except Exception as e:
            logging.error(f"Error saving report to {output_path}: {str(e)}")
