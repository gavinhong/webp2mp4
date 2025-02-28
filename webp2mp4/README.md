# WebP to MP4 Converter

A Python application to batch convert WebP files to MP4 format.

## Features

- Select multiple WebP files for batch conversion
- **Native drag and drop support** for easy file selection
- Set custom frames per second (FPS) for the output videos
- Choose a custom output directory or use the same directory as the input files
- Progress tracking for each conversion
- Support for both animated and static WebP files
- Simple and intuitive graphical user interface

## Project Structure

The project follows a modular architecture with high cohesion and loose coupling:

- `main/core/`: Core conversion logic
- `main/ui/`: User interface components
- `main/utils/`: Utility functions and helpers

## Requirements

- Python 3.6 or higher
- Pillow (Python Imaging Library)
- MoviePy

## Installation

### Option 1: Using pip

```bash
# Install the basic package
pip install -e .

# To include drag and drop support
pip install -e .[dnd]
```

### Option 2: Using conda

```bash
# Create a conda environment
conda create -n webp2mp4 python=3.10
conda activate webp2mp4

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the application

```bash
# If installed with pip
webp2mp4

# Or run directly
python -m webp2mp4

# Or use the launcher script
python run.py

# Or use the standalone executable (Windows)
WebP2MP4_Converter.exe
```

### Using the application

1. Click "Select WebP Files" to choose the WebP files you want to convert
2. **Or drag and drop WebP files directly into the application window**
3. Set the desired FPS (frames per second) for the output videos
4. Choose an output directory or leave as "Same as input" to save in the same location as the input files
5. Click "Convert to MP4" to start the conversion process
6. The progress bar will show the overall progress, and the status label will show the current operation

## How It Works

The converter works by:
1. Extracting each frame from the WebP file
2. Saving each frame as a temporary PNG file
3. Using MoviePy to combine the frames into an MP4 video
4. Cleaning up the temporary files

## Notes

- The conversion process can be slow for files with many frames
- The application supports both animated and static WebP files
- The output videos use the H.264 codec for maximum compatibility
- The standalone executable includes native drag and drop functionality without requiring additional packages
