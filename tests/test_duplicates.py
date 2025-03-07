from icecream import ic
from viz_scout import DuplicateDetector


def test_get_exact_duplicates():
    minio_config = {
        "endpoint": "<IP>:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "secure":False,
        "bucket":"rohan"
    }

    detector = DuplicateDetector(dataset_path="1054/images", store="minio", minio_config=minio_config)
    # detector = DuplicateDetector(dataset_path="sample_datasets/coco20", store="local")

    exact_duplicates = detector.get_exact_duplicates()
    near_duplicates = detector.get_near_duplicates()
    # assert duplicates == {"image1.png": ["image2.png"]}

    ic.enable()
    ic(exact_duplicates)
    ic(near_duplicates)
    ic.disable()