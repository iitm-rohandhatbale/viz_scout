import os
from reprlib import recursive_repr
import boto3

from icecream import ic
from minio import Minio
from io import BytesIO
from tqdm import tqdm
from .corruption import CorruptionDetector


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
        self.corruption_detcetor = CorruptionDetector()

    def _load_from_local(self) -> tuple:

        def load_file(file):
            with open(file, "rb") as f:
                file_stream = BytesIO(f.read())
                file_stream.seek(0)
                return file_stream

        try:

            if not os.path.exists(self.source):
                raise ValueError(f"Local path does not exist: {self.source}")
            ic(f"Loading images from local directory: {self.source}")

            image_files = [
                file for file in os.listdir(self.source)
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ]

            images = {
                os.path.join(self.source, file): load_file(os.path.join(self.source, file))
                for file in image_files if not self.corruption_detcetor.is_corrupt(os.path.join(self.source, file))
            }
            
            images = {}
            corrupt_images = []
            for file in image_files:
                if not self.corruption_detcetor.is_corrupt(os.path.join(self.source, file)):
                    images[os.path.join(self.source, file)] = load_file(
                        os.path.join(self.source, file))
                else:
                    corrupt_images.append(os.path.join(self.source, file))
                
            ic(f"Successfully loaded {len(images)} images from local directory.")
            return (images, corrupt_images)
        except Exception as e:
            ic(f"Error loading images from local directory: {e}")
            raise

    def _load_from_s3(self) -> tuple:
        try:
            if not self.s3_config:
                raise ValueError("S3 configuration is required for loading from S3.")

            ic("Initializing S3 client...")

            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.s3_config["access_key"],
                aws_secret_access_key=self.s3_config["secret_key"],
                region_name=self.s3_config["region"],
            )

            bucket = self.s3_config["bucket"]
            ic(f"Listing objects in S3 bucket: {bucket}")
            objects = s3.list_objects_v2(Bucket=bucket).get("Contents", [])
            files = {}
            corrupt_files = []
            for obj in tqdm(objects, desc="Streaming images from S3"):
                key = obj["Key"]
                try:
                    if key.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        # Stream the file directly from S3
                        file_stream = BytesIO()
                        s3.download_fileobj(bucket, key, file_stream)
                        file_stream.seek(0)
                        files[key] = file_stream
                except Exception as e:
                    corrupt_files.append(key)
            ic(f"Successfully loaded {len(files)} images from S3 bucket.")
            return (files, corrupt_files)
        except Exception as e:
            ic(f"Error loading images from S3: {e}")
            raise

    def _load_from_minio(self) -> dict:
        try:
            if not self.minio_config:
                raise ValueError("MinIO configuration is required for loading from MinIO.")

            ic("Initializing MinIO client...")
            client = Minio(
                endpoint=self.minio_config["endpoint"],
                access_key=self.minio_config["access_key"],
                secret_key=self.minio_config["secret_key"],
                secure=self.minio_config.get("secure", False),
            )

            bucket = self.minio_config["bucket"]
            ic(f"Listing objects in MinIO bucket: {bucket}")
            objects = client.list_objects(bucket, prefix=self.source, recursive=True)
            
            files = {}
            corrupt_images = []

            for obj in tqdm(objects, desc="Streaming images from MinIO"):
                key = obj.object_name
                if key.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    try:
                    # Stream the file directly from MinIO
                        response = client.get_object(bucket, key)
                        file_stream = BytesIO(response.read())
                        file_stream.seek(0)
                        
                        # Corruption check
                        if not self.corruption_detcetor.is_corrupt(file_stream):
                            files[key] = file_stream
                        else:
                            corrupt_images.append(key)
                            
                        response.close()
                        response.release_conn()
                    except Exception as file_error:
                        ic(f"Error loading file {key}: {file_error}")
                        corrupt_images.append(key)
                    

            ic(f"Successfully loaded {len(files)} images from MinIO bucket.")
            return (files, None)
        except Exception as e:
            ic(f"Error loading images from MinIO: {e}")
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
            ic(f"Error loading images: {e}")
            raise

    def cleanup(self):
        """
        Cleanup if needed (no temporary files for streaming).
        """
        ic("No cleanup actions required for the current implementation.")
        pass
