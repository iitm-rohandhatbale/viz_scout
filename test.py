from random import randint
from icecream import ic



if __name__ == "__main__":
    
    # import random
    # with open("/Users/rohandhatbale/office_work/viz_scout/sample_datasets/coco20/000000000025.jpg", "rb") as f:
    #     data = bytearray(f.read())
    
    # for _ in range(10):
    #     index = random.randint(0, len(data)-1)
    #     data[index] = 0xFF
    
    # with open("/Users/rohandhatbale/office_work/viz_scout/sample_datasets/coco5/rohan.jpg", "wb") as f:
    #     pass
        
    
    
    from tests.test_dataset import test_dataset_loader
    test_dataset_loader()

    from tests.test_duplicates import test_get_exact_duplicates
    test_get_exact_duplicates()
    #
    # from tests.test_quality import test_image_quality_analyzer
    # test_image_quality_analyzer()

    from tests.test_eda_report import test_generate_eda_report
    test_generate_eda_report()
    
    # from tests.test_eda_plots import *
    # test_get_image_size_distribution()


