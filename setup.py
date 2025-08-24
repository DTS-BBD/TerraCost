from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except (FileNotFoundError, UnicodeDecodeError):
        return "TerraCost - Multi-cloud Terraform cost estimation and AI-powered optimization tool"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except (FileNotFoundError, UnicodeDecodeError):
        # Fallback requirements if file can't be read
        return [
            "numpy>=1.21.0",
            "requests>=2.25.0",
            "pydantic>=2.0.0",
            "boto3>=1.26.0",
            "langchain>=0.3.0",
            "langchain-openai>=0.3.0",
            "python-dotenv>=1.0.0",
        ]

setup(
    name="terracost",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="TerraCost - Multi-cloud Terraform cost estimation and AI-powered optimization tool",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/terracost",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/terracost/issues",
        "Documentation": "https://github.com/yourusername/terracost#readme",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "terracost=terracost.main:main",
        ],
    },
    keywords="terraform, cost-estimation, aws, azure, gcp, cloud-costs, infrastructure",
    license="MIT",
    zip_safe=False,
)
