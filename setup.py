from setuptools import setup, find_packages

setup(
    name="grafana_mcp",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "grafana_mcp": ["dashboard.json"],
    },
    install_requires=[
        "fastmcp>2.3",
        "grafana-client>=4.3.2",
        "python-dotenv>=1.1.0",
        "requests>=2.31",
    ],
    python_requires=">=3.7",
)