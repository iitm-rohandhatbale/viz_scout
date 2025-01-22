from icecream import ic

from viz_scout.eda_report import EDAReport


def test_generate_eda_report():
    dataset_path = "sample_datasets/coco5"
    report_generator = EDAReport(dataset_path=dataset_path, duplicate_check=True)

    report = report_generator.generate_report()
    ic.enable()
    ic(report)
    ic.disable()
