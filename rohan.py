from minio import Minio
from tqdm import tqdm
from io import BytesIO
from icecream import ic

minio_config = {
    "endpoint": "10.11.0.5:9000",
    "access_key": "minioadmin",
    "secret_key": "minioadmin",
    "secure":False,
    "bucket":"rohan"
}

client = Minio(
    endpoint=minio_config["endpoint"],
    access_key=minio_config["access_key"],
    secret_key=minio_config["secret_key"],
    secure=minio_config.get("secure", False)
    )

source = "1054/images"
bucket = minio_config["bucket"]
objects = client.list_objects(bucket, prefix=source, recursive=True)

files = {}

for obj in tqdm(objects, desc="Streaming images from MinIO"):
    key = obj.object_name
    print(key)
    if key.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
        try:
            # Stream the file directly from MinIO
            response = client.get_object(bucket, key)
            file_stream = BytesIO(response.read())
            file_stream.seek(0)
            files[key] = file_stream
            response.close()
            response.release_conn()
        except Exception as file_error:
            ic(f"Error loading file {key}: {file_error}")


print(f"{files = }")