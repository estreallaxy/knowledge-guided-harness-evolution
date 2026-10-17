#!/usr/bin/env python3
"""
Setup script for DPDKTokenizer Python components
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), '..', '..', 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "DPDKTokenizer Python components"

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="dpdk-tokenizer",
    version="1.0.0",
    author="XXXXXX",
    author_email="XXX@XXX.com",
    description="High-performance tokenizer with DPDK and vector database integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/XXXXXX",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
        "full": [
            "sentence-transformers>=2.2.0",
            "transformers>=4.20.0",
            "torch>=1.12.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "dpdk-tokenizer-chromadb=examples.example_chromadb:main",
            "dpdk-tokenizer-pgvector=examples.example_pgvector:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="dpdk, tokenizer, vector-database, chromadb, pgvector, postgresql, nlp, high-performance",
    project_urls={
        "Bug Reports": "https://github.com/XXXX",
        "Source": "https://github.com/XXXX",
        "Documentation": "https://github.com/XXXX",
    },
)
