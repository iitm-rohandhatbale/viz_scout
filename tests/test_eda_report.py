from icecream import ic

from viz_scout.eda_report import EDAReport


def test_generate_eda_report():
    minio_config = {
        "endpoint": "<IP>:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "secure":False,
        "bucket":"rohan"
    }
    
    # report_generator = EDAReport(dataset_path="sample_datasets/coco5", duplicate_check=True, store="local")
    report_generator = EDAReport(dataset_path="1054/images", duplicate_check=True, store="minio", minio_config=minio_config)


    report = report_generator.generate_report()
    ic.enable()
    ic(report)
    ic.disable()
