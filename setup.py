from setuptools import setup, find_packages

setup(
    name="grafana_mcp",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "mcp>=1.3.0",
    ],
    python_requires=">=3.7",
)