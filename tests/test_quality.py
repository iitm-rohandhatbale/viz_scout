import cv2
from io import BytesIO
from PIL import Image
from icecream import ic

from viz_scout.quality import ImageQualityAnalyzer

def test_image_quality_analyzer():
    image_path = "sample_datasets/coco5/000000000049.jpg"

    quality_analyzer = ImageQualityAnalyzer()

    brightness_score = quality_analyzer.brightness_score(image_path)
    ic(brightness_score)

    np_image = cv2.imread(image_path)
    darkness_score = quality_analyzer.darkness_score(np_image)
    ic(darkness_score)

    pil_image = Image.open(image_path)
    blur_score = quality_analyzer.blur_score(pil_image)
    ic(blur_score)

    with open(image_path, "rb") as f:
        file_stream = BytesIO(f.read())
        file_stream.seek(0)
    uniformity_score = quality_analyzer.uniformity_score(file_stream)
    ic(uniformity_score)





