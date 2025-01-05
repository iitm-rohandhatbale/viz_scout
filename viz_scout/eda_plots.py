import os
import json
import io
import logging
from re import S

import pandas as pd
import numpy as np
import altair as alt

from .eda_report import EDAReport
from .dataset import DatasetLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ChartBase:
    def __init__(self, chart):
        if not isinstance(chart, (alt.Chart, alt.LayerChart, alt.HConcatChart, alt.VConcatChart)):
            raise (
                "plot should be of type [alt.Chart, alt.LayerChart, alt.HConcatChart, alt.VConcatChart]")
        self.chart = chart
    
    def to_json(self):
        return json.loads(self.chart.to_json())
    
    def plot(self):
        return self.chart
    
    def save(self, save_dir = os.getcwd(), file_name="chart", file_format="png", inline=False, ppi=72, scale_factor=1):
        acceptable_file_formats = ["png", "pdf", "svg", "html"]
        if file_format.lower().strip('.') not in acceptable_file_formats:
            raise f"File format should be in {acceptable_file_formats}"
    
        file_savepath = os.path.join(save_dir, f"{file_name.strip('.')}.{file_format.strip('.')}")
        
        if file_format.lower().strip('.') == "png":    
            self.chart.save(file_savepath, ppi=ppi, scale_factor=scale_factor)
        elif file_format.lower().strip('.') == "html":
            self.chart.save(file_savepath, inline=inline)
        else:
            self.chart.save(file_savepath)
            
        logging.info(f"Chart/Plot saved successfully at {file_savepath}")
    



class EDAPlots:
    def __init__(self, dataset_path: str = None, data_df: pd.DataFrame = None):
        args = {"dataset_path": dataset_path, "data_df": data_df}
        non_none_args = [key for key, value in args.items() if value is not None]
        
        if len(non_none_args) != 1:
            raise ValueError(
                f"Exactly one argument must be provided, but got {len(non_none_args)}: {non_none_args}")
        
        self.dataset_path = dataset_path
        self.data_df = data_df

        
        if self.dataset_path is not None:
            self._load_dataset()
            
        
        
    def _load_dataset(self):
        report_generator = EDAReport(dataset_path=self.dataset_path, duplicate_check=False)
        image_stats = None
        if len(report_generator.images) < 1000:
            logging.info("Processing image-level statistics sequentially...")
            # Image-level statistics with sequential processing
            image_stats = report_generator._get_image_stats()
        else:
            logging.info("Processing image-level statistics in parallel...")
            # Image-level statistics with parallel processing
            image_stats = report_generator._get_image_stats_parallel()
            
        self.data_df = pd.DataFrame(image_stats)
        
    
    def get_image_size_distribution(self):
        """
        Generates histograms for image width and height.
        """
        width_hist = alt.Chart(self.data_df).mark_bar().encode(
            alt.X('img_width', bin=alt.Bin(maxbins=20), title='Image Width'),
            alt.Y('count()', title='Frequency'),
            tooltip=['img_width', 'count()']
        ).properties(
            title="Image Width Distribution"
        ).interactive()

        height_hist = alt.Chart(self.data_df).mark_bar().encode(
            alt.X('img_height', bin=alt.Bin(maxbins=20), title='Image Height'),
            alt.Y('count()', title='Frequency'),
            tooltip=['img_height', 'count()']
        ).properties(
            title="Image Height Distribution"
        ).interactive()
        
        combined_chart = width_hist | height_hist
        
        return ChartBase(chart=combined_chart)
    
    def get_aspect_ratio_distribution(self):
        """
        Generates a histogram for aspect ratio distribution.
        """
        self.data_df['aspect_ratio'] = self.data_df.img_width / self.data_df.img_height
        
        chart = alt.Chart(self.data_df).mark_bar().encode(
            alt.X('aspect_ratio', bin=alt.Bin(
                maxbins=20), title='Aspect Ratio'),
            alt.Y('count()', title='Frequency'),
            tooltip=['aspect_ratio', 'count()']
        ).properties(
            title="Aspect Ratio Distribution"
        ).interactive()

        return ChartBase(chart=chart)
    
    def get_width_height_correlation(self):
        """
        Generates a scatter plot for the correlation between image width and height.
        """
        chart = alt.Chart(self.data_df).mark_circle(size=60).encode(
            alt.X('img_width', title='Image Width'),
            alt.Y('img_height', title='Image Height'),
            tooltip=['img_width', 'img_height']
        ).properties(
            title="Width vs Height Correlation"
        ).interactive()

        return ChartBase(chart)
    
    def get_resolution_distribution(self):
        """
        Generates a histogram for image resolution (total pixels = width * height).
        """
        self.data_df['resolution'] = self.data_df['img_width'] * self.data_df['img_height']

        chart = alt.Chart(self.data_df).mark_bar().encode(
            alt.X('resolution', bin=alt.Bin(maxbins=20),
                  title='Image Resolution (Width x Height)'),
            alt.Y('count()', title='Frequency'),
            tooltip=['resolution', 'count()']
        ).properties(
            title="Image Resolution Distribution"
        ).interactive()

        return ChartBase(chart)
    
    
        
            
        
            
            
            

    
        
        



        
