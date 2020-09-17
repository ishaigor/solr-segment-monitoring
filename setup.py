from setuptools import setup, find_packages
setup(
    name = "segment-metrics",
    version = 1.1,
    packages = find_packages(),
    python_requires = ">=3",
    install_requires=["multidict>=4.7.5", "regex>=2020.4.4", "python-dateutil>=2.8.1", "request>=2.23.0", "click>=6.7", "prometheus_client>=0.7.1"]
)