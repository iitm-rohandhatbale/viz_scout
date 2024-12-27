import os
import boto3
import logging

from minio import Minio
from io import BytesIO
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DatasetLoader:
    def __init__(self, source, minio_config=None, s3_config=None):
        """
        Initialize the dataset loader.


        Args:
            source (str): Path to the dataset, can be local path or S3/MinIO URI.
            minio_config (dict): MinIO configuration with keys: endpoint, access_key, secret_key.
            s3_config (dict): S3 configuration with keys: bucket, access_key, secret_key, region.
        """
        self.source = source
        self.minio_config = minio_config
        self.s3_config = s3_config

    def _load_from_local(self) -> dict:

        def load_file(file):
            with open(file, "rb") as f:
                file_stream = BytesIO(f.read())
                file_stream.seek(0)
                return file_stream

        try:

            if not os.path.exists(self.source):
                raise ValueError(f"Local path does not exist: {self.source}")
            logging.info(f"Loading images from local directory: {self.source}")

            image_files = [
                file for file in os.listdir(self.source)
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ]

            images = {
                os.path.join(self.source, file): load_file(os.path.join(self.source, file))
                for file in image_files
            }
            logging.info(f"Successfully loaded {len(images)} images from local directory.")
            return images
        except Exception as e:
            logging.error(f"Error loading images from local directory: {e}")
            raise

    def _load_from_s3(self) -> dict:
        try:
            if not self.s3_config:
                raise ValueError("S3 configuration is required for loading from S3.")

            logging.info("Initializing S3 client...")

            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.s3_config["access_key"],
                aws_secret_access_key=self.s3_config["secret_key"],
                region_name=self.s3_config["region"],
            )

            bucket = self.s3_config["bucket"]
            logging.info(f"Listing objects in S3 bucket: {bucket}")
            objects = s3.list_objects_v2(Bucket=bucket).get("Contents", [])
            files = {}

            for obj in tqdm(objects, desc="Streaming images from S3"):
                key = obj["Key"]
                if key.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    # Stream the file directly from S3
                    file_stream = BytesIO()
                    s3.download_fileobj(bucket, key, file_stream)
                    file_stream.seek(0)
                    files[key] = file_stream
            logging.info(f"Successfully loaded {len(files)} images from S3 bucket.")
            return files
        except Exception as e:
            logging.error(f"Error loading images from S3: {e}")
            raise

    def _load_from_minio(self) -> dict:
        try:
            if not self.minio_config:
                raise ValueError("MinIO configuration is required for loading from MinIO.")

            logging.info("Initializing MinIO client...")
            client = Minio(
                endpoint=self.minio_config["endpoint"],
                access_key=self.minio_config["access_key"],
                secret_key=self.minio_config["secret_key"],
                secure=self.minio_config.get("secure", False),
            )

            bucket = self.minio_config["bucket"]
            logging.info(f"Listing objects in MinIO bucket: {bucket}")
            objects = client.list_objects(bucket, recursive=True)
            files = {}

            for obj in tqdm(objects, desc="Streaming images from MinIO"):
                key = obj.object_name
                if key.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    # Stream the file directly from MinIO
                    file_stream = BytesIO()
                    client.fget_object(bucket, key, file_stream)
                    file_stream.seek(0)
                    files[key] = file_stream

            logging.info(f"Successfully loaded {len(files)} images from MinIO bucket.")
            return files
        except Exception as e:
            logging.error(f"Error loading images from MinIO: {e}")
            raise

    def load_images(self) -> dict:
        """
        Load images from the specified source.


        Returns:
            dict: dict of BytesIO streams containing image data as value and image name/image path as key.
        """
        try:
            if self.source.startswith("s3://"):
                return self._load_from_s3()
            elif self.source.startswith("minio://"):
                return self._load_from_minio()
            else:
                return self._load_from_local()
        except Exception as e:
            logging.error(f"Error loading images: {e}")
            raise

    def cleanup(self):
        """
        Cleanup if needed (no temporary files for streaming).
        """
        logging.info("No cleanup actions required for the current implementation.")
        pass
