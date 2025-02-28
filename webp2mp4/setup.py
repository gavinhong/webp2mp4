"""
Setup script for the WebP to MP4 converter
"""

from setuptools import setup, find_packages

setup(
    name="webp2mp4",
    version="0.1.0",
    description="A utility to convert WebP files to MP4 format",
    author="kai",
    packages=find_packages(),
    install_requires=[
        "pillow>=9.0.0",
        "moviepy>=1.0.3",
        "imageio>=2.9.0",
        "imageio-ffmpeg>=0.4.5",
        "numpy>=1.19.0",
        "decorator>=4.4.2",
        "proglog>=0.1.9",
        "tqdm>=4.56.0",
    ],
    extras_require={
        "gui": ["tkinterdnd2>=0.3.0"],
    },
    entry_points={
        "console_scripts": [
            "webp2mp4=webp2mp4.__main__:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Graphics :: Conversion",
    ],
)
