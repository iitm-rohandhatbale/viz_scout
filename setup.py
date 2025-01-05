from setuptools import setup, find_packages

setup(
    name="viz_scout",  
    version="0.2.1",  
    author="Rohan Dhatbale",
    author_email="rohandhatbale@gmail.com",
    description="A Python toolkit for end-to-end image analysis with cloud (Minio, S3) support.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/iitm-rohandhatbale/viz_scout",  
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",  # Minimum Python version
    install_requires=[
        "opencv-python",
        "numpy",
        "tqdm",
        "pillow",
        "boto3",
        "minio",
        "imagededup",
        "icecream", 
        "altair",
        "pandas",
        "vl-convert-python"
    ]
)
