"""
Setup script for llm_validator package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Читаем README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Читаем requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, encoding="utf-8") as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="llm-validator",
    version="1.0.0",
    author="Legal Tech Team",
    author_email="team@yourise.app",
    description="Модуль для проверки юридической легальности изменений в документах",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourise/llm-validator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Legal",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "responses>=0.22.0",
        ],
        "postgres": [
            "psycopg2-binary>=2.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-validate=llm_validator.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
