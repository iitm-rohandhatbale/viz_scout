from icecream import ic
from viz_scout.dataset import DatasetLoader


def test_dataset_loader():
    dataset_path = "sample_datasets/coco5"

    dataset_loader = DatasetLoader(source=dataset_path)
    images, corrupt_images= dataset_loader.load_images()

    ic.enable()
    ic(images)
    ic(corrupt_images)
    ic.disable()