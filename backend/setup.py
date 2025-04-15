from setuptools import setup, find_packages

setup(
    name="greenbite-backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask==2.0.1",
        "flask-cors==3.0.10",
        "pandas==1.3.3",
        "thefuzz==0.19.0",
        "python-Levenshtein==0.12.2",
        "scikit-learn==0.24.2",
        "numpy==1.21.2",
        "gunicorn==20.1.0",
        "google-cloud-storage==2.7.0"
    ],
    python_requires=">=3.9",
) 