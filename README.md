<h1 align="center">
  <img src="logo.webp" width="250" height="250" alt="VizScout">
</h1>


# VizScout


**VizScout** is a Python package for advanced image data analysis and correction. It provides utilities for detecting and analyzing image quality, identifying duplicates, checking for corrupt images, and generating exploratory data analysis (EDA) reports on datasets. The package is designed to handle datasets stored locally, in AWS S3, or MinIO for large-scale data processing.


---


## Features


- **Image Data Quality Analysis**: Evaluate the quality of images based on brightness, blur, and uniformity.
- **Duplicate Image Detection**: Identify exact and near-duplicate images in a dataset.
- **Corruption Detection**: Automatically detect corrupt images that cannot be read or processed.
- **Exploratory Data Analysis (EDA)**: Generate detailed reports on dataset-level and image-level statistics.
- **Support for Large Datasets**: Efficient handling of large datasets using parallel processing and batch loading.


---


## Installation


To install `viz_scout`, use pip:


```bash
pip install viz_scout
````


Alternatively, clone the repository and install manually:


```bash
git clone https://github.com/yourusername/viz_scout.git
cd viz_scout
pip install .
```

for Apple Macbook M1 (Silicon)

```bash
conda install scipy numpy matplotlib
conda install --channel=conda-forge scikit-learn

```
Then install remaining libraries
---


## Dependencies


- Python 3.6+
- Pillow - for image handling
- opencv-python - for image processing tasks like blur detection
- numpy - for numerical operations
- boto3 - for interacting with AWS S3 (if using S3 buckets)
- minio - for interacting with MinIO (if using MinIO)


You can install the required dependencies using:
```bash
pip install -r requirements.txt
```


---


## Usage


**1. Basic Example: Analyzing a Local Dataset**


```python
from viz_scout import EDAReport


# Initialize the EDA report generator for a local dataset
eda = EDAReport(
    dataset_path="path/to/dataset",
    duplicate_check=True,
    blur_threshold=5
)


# Generate the report
report = eda.generate_report()


# Print the report
print(json.dumps(report, indent=4))


# Optionally save the report to a file
eda.save_report(report, output_path="dataset_eda_report.json")
```  


**2. Advanced Example: Analyzing an AWS S3 Dataset**  
To analyze datasets stored on S3 or MinIO, provide the relevant configuration:


```python
from viz_scout import EDAReport


# Example for S3
eda = EDAReport(
    dataset_path="s3://my-bucket/dataset/",
    s3_config={
        "access_key": "your-access-key",
        "secret_key": "your-secret-key",
        "region": "your-region",
    },
    duplicate_check=True,
    blur_threshold=5
)


# Generate the report
report = eda.generate_report()


# Print or save the report
print(json.dumps(report, indent=4))
eda.save_report(report, output_path="s3_eda_report.json")


########################################################


# Example for MinIO
eda = EDAReport(
    dataset_path="minio://my-bucket/dataset/",
    minio_config={
        "endpoint": "minio-server-url",
        "access_key": "your-access-key",
        "secret_key": "your-secret-key",
    },
    duplicate_check=True,
    blur_threshold=5
)


# Generate the report
report = eda.generate_report()


# Print or save the report
print(json.dumps(report, indent=4))
eda.save_report(report, output_path="minio_eda_report.json")
```


**3. Parallel Processing and Batch Loading for large dataset**  
When processing large datasets with hundreds of thousands of images, you can enable parallel processing for faster results:


```python
from viz_scout import EDAReport


eda = EDAReport(
    dataset_path="path/to/large/dataset",
    batch_size=200,  # Process in batches of 200 images at a time
    num_workers=8    # Use 8 parallel workers (threads)
)


# Generate the report
report = eda.generate_report()


# Print or save the report
print(json.dumps(report, indent=4))
eda.save_report(report, output_path="large_dataset_eda_report.json")
```


## Key Functions and Methods


#### `EDAReport`: The main class for generating EDA reports on image datasets.


- `__init__(self, dataset_path, minio_config=None, s3_config=None, corrupt_check=True, blur_threshold=3, batch_size=100, num_workers=4)`
    - Initializes the EDA report generator.  
    - Supports local, S3, or MinIO datasets.  
    - Customizes corruption checks, blur thresholds, batch size, and parallel processing.




- `generate_report()`
  - Generates an EDA report containing both dataset-level and image-level statistics.
  - Returns the report as a dictionary.




- `save_report(report, output_path)`
  - Saves the generated report to a JSON file at the specified output path (`.json` format).




#### `ImageQualityAnalyzer`: A class for analyzing image quality based on brightness, blur, and uniformity.
- `brightness_score(image)`
  - Returns a score (0-10) indicating the brightness of the image.




- `blur_score(image)`
  - Returns a score (0-10) indicating the blur level of the image.




- `uniformity_score(image)`
  - Returns a score (0-10) indicating the uniformity of the image.


#### `DuplicateDetector`: A class for detecting exact and near-duplicate images in a dataset.
 
- `get_exact_duplicates(images)`
  - Returns a list of exact duplicate images from the dataset.




#### `CorruptionDetector`: A class for detecting corrupt images in a dataset.


- `is_corrupt(image)`
    - Returns True if the image is corrupt or unreadable.


## Performance Optimizations
- **Parallel Processing**: The package supports parallel processing via ThreadPoolExecutor to handle large datasets efficiently.
- **Batch Processing**: Process images in batches to avoid memory overload.
- **Lazy Loading**: Images are processed on-demand to minimize memory usage.


---
## Contributing
We welcome contributions to viz_scout! If you'd like to contribute, please follow these steps:


    1. Fork the repository.
    2. Create a new branch.
    3. Make your changes.
    4.Write tests to cover your changes (if applicable).
    5. Submit a pull request.


---
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.


---


## Contact
For any questions or issues, please open an issue on GitHub or contact [rohandhatbale@gmail.com].







