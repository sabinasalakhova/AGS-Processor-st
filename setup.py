from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ags-processor-st",
    version="0.1.0",
    author="Sabina Salakhova",
    description="AGS3/AGS4 processor for geotechnical data with data quality focus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-ags4>=0.4.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "xlsxwriter>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ags-processor=ags_processor.cli:main",
        ],
    },
)
