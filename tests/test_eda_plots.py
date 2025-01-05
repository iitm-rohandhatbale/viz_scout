from email.mime import image
from icecream import ic
from viz_scout.eda_plots import EDAPlots


def test_get_image_size_distribution():
    plot_generator = EDAPlots(
        dataset_path="/Users/rohandhatbale/office_work/viz_scout/sample_datasets/coco20")
    
    save_dir = "/Users/rohandhatbale/office_work/viz_scout/trial_notebooks"
    
    img_size_distribution = plot_generator.get_image_size_distribution()
    ic(img_size_distribution.to_json())
    ic(type(img_size_distribution.plot()))
    img_size_distribution.save(
        save_dir=save_dir, 
        file_name="img_size_distribution",
        file_format="png"
        )
    
    aspect_ratio_distribution = plot_generator.get_aspect_ratio_distribution()
    aspect_ratio_distribution.save(
        save_dir=save_dir, 
        file_name="aspect_ratio_distribution", 
        file_format="pdf"
        )
    
    width_height_correlation = plot_generator.get_width_height_correlation()
    width_height_correlation.save(
        save_dir=save_dir,
        file_name="width_height_correlation",
        file_format="html"
    )
    
    


