from icecream import ic
from viz_scout import DuplicateDetector


def test_get_exact_duplicates():
    detector = DuplicateDetector(dataset_path="sample_datasets/coco20")

    exact_duplicates = detector.get_exact_duplicates()
    near_duplicates = detector.get_near_duplicates()
    # assert duplicates == {"image1.png": ["image2.png"]}

    ic.enable()
    ic(exact_duplicates)
    ic(near_duplicates)
    ic.disable()