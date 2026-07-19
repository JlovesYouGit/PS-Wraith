#!/usr/bin/env python3
"""
Setup script for SpectrumAnalyzer Pro
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="spectrum-analyzer-pro",
    version="1.0.0",
    author="SpectrumAnalyzer Pro Team",
    author_email="support@spectrumanalyzer-pro.com",
    description="Professional WiFi Spectrum Analysis and Network Testing Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JlovesYouGit/SpectrumAnalyzer-Pro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.4',
            'pytest-cov>=4.1',
            'black>=24.4',
            'ruff>=0.4.0',
            'mypy>=1.10',
            'pre-commit>=3.7',
        ],
        'build': [
            'pyinstaller>=5.0',
            'setuptools>=65.0',
            'wheel>=0.38',
        ],
    },
    entry_points={
        'console_scripts': [
            'spectrum-analyzer-pro=main:main',
            'spectrum-pro=main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.yaml', '*.yml'],
        'spectrum_analysis': ['*.py', '*.bat', '*.ps1'],
        'spectrum_grabber': ['*.py'],
    },
    project_urls={
        "Bug Reports": "https://github.com/JlovesYouGit/SpectrumAnalyzer-Pro/issues",
        "Source": "https://github.com/JlovesYouGit/SpectrumAnalyzer-Pro",
        "Documentation": "https://github.com/JlovesYouGit/SpectrumAnalyzer-Pro/blob/main/README.md",
    },
    keywords="wifi spectrum analysis network testing monitoring",
    zip_safe=False,
)
