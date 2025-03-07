from icecream import ic
from viz_scout.dataset import DatasetLoader


def test_dataset_loader():
    dataset_path = "1054/images"

    minio_config = {
        "endpoint": "<IP>:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "secure":False,
        "bucket":"rohan"
    }

    dataset_loader = DatasetLoader(source=dataset_path, store="minio", minio_config=minio_config)
    images, corrupt_images= dataset_loader.load_images()

    ic.enable()
    ic(images)
    ic(corrupt_images)
    ic.disable()