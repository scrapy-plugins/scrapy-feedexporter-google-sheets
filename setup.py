from setuptools import find_packages, setup

setup(
    name="scrapy_google_sheets_exporter",
    version="0.0.1",
    description="Scrapy Feed Exporter for Google Sheets",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gspread",
        "scrapy"
    ],
)
