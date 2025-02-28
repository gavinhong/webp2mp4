"""
WebP to MP4 Converter Core Module
Handles the actual conversion logic from WebP to MP4
"""

import os
import sys
import shutil
import tempfile
from PIL import Image
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

class WebPConverter:
    """
    Core class for converting WebP files to MP4 format.
    Handles both animated and static WebP files.
    """
    
    @staticmethod
    def detect_fps(path):
        """
        Detect the FPS of a WebP file.
        
        Args:
            path (str): Path to the WebP file
            
        Returns:
            float: Detected FPS or 20 as default if detection fails
        """
        try:
            # Open the WebP file
            with Image.open(path) as img:
                # Check if it's animated
                try:
                    img.seek(1)  # Try to move to the second frame
                    # It's animated, try to get the duration of frames
                    durations = []
                    current_frame = 0
                    
                    # Reset to first frame
                    img.seek(0)
                    
                    # Collect durations of frames
                    while True:
                        try:
                            # Get duration in milliseconds
                            duration = img.info.get('duration', 100)  # Default to 100ms if not specified
                            durations.append(duration)
                            current_frame += 1
                            img.seek(current_frame)
                        except EOFError:
                            break
                    
                    # Calculate average duration in seconds
                    if durations:
                        avg_duration = sum(durations) / len(durations) / 1000.0  # Convert to seconds
                        if avg_duration > 0:
                            fps = 1.0 / avg_duration
                            return fps
                
                except EOFError:
                    # Not animated, default to 20 FPS for static images
                    pass
        
        except Exception as e:
            pass
        
        # Default FPS if detection fails
        default_fps = 20.0
        return default_fps
    
    @staticmethod
    def analyse_image(path):
        """
        Analyze the WebP image to determine if it uses partial updates.
        
        Args:
            path (str): Path to the WebP file
            
        Returns:
            dict: Analysis results including size and mode
        """
        im = Image.open(path)
        results = {
            'size': im.size,
            'mode': 'full',
        }
        try:
            while True:
                if im.tile:
                    tile = im.tile[0]
                    update_region = tile[1]
                    update_region_dimensions = update_region[2:]
                    if update_region_dimensions != im.size:
                        results['mode'] = 'partial'
                        break
                im.seek(im.tell() + 1)
        except EOFError:
            pass
        return results
    
    @staticmethod
    def process_image(path, temp_dir, status_callback=None):
        """
        Extract frames from the WebP file.
        
        Args:
            path (str): Path to the WebP file
            temp_dir (str): Directory to store temporary frame images
            status_callback (callable, optional): Callback function for status updates
            
        Returns:
            list: List of paths to extracted frame images
        """
        images = []
        try:
            mode = WebPConverter.analyse_image(path)['mode']
            
            im = Image.open(path)
            
            i = 0
            p = im.getpalette()
            last_frame = im.convert('RGBA')
            
            try:
                while True:
                    basename = os.path.basename(path)
                    output_folder = temp_dir
                    frame_file_name = os.path.join(output_folder, f'{os.path.splitext(basename)[0]}-{i}.png')
                    
                    # Update status with frame info
                    if status_callback:
                        status_callback(f"Processing frame {i} of {os.path.basename(path)}")
                    
                    if '.gif' in path.lower():
                        if not im.getpalette():
                            im.putpalette(p)
                    
                    new_frame = Image.new('RGBA', im.size)
                    
                    if mode == 'partial':
                        new_frame.paste(last_frame)
                    
                    new_frame.paste(im, (0, 0), im.convert('RGBA'))
                    
                    new_frame.save(frame_file_name, 'PNG')
                    images.append(frame_file_name)
                    i += 1
                    last_frame = new_frame
                    im.seek(im.tell() + 1)
            except EOFError:
                # Update status with completion info
                if status_callback and i > 0:
                    status_callback(f"Extracted all {i} frames from {os.path.basename(path)}")
                pass
        except Exception as e:
            import traceback
            traceback.print_exc()
            # If we have at least one frame, we can continue
            if not images:
                raise
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
            
        return images
    
    @staticmethod
    def convert(input_file, output_file=None, fps=None, status_callback=None):
        """
        Convert WebP to MP4.
        
        Args:
            input_file (str): Path to the input WebP file
            output_file (str, optional): Path to the output MP4 file. If None, uses the same name as input with .mp4 extension
            fps (float, optional): Frames per second for the output video. If None, will be detected from source.
            status_callback (callable, optional): Callback function for status updates
            
        Returns:
            str: Path to the created MP4 file
            
        Raises:
            ValueError: If no frames could be extracted from the WebP file
            Exception: For any other errors during conversion
        """
        if output_file is None:
            output_file = os.path.splitext(input_file)[0] + '.mp4'
            
        temp_dir = tempfile.mkdtemp()
        try:
            if status_callback:
                status_callback(f"Extracting frames from {os.path.basename(input_file)}")
            
            # Check if file is a valid WebP
            is_animated = False
            try:
                with Image.open(input_file) as img:
                    # Check if it's animated
                    try:
                        img.seek(1)
                        is_animated = True
                        img.seek(0)
                    except EOFError:
                        is_animated = False
            
            except Exception as e:
                raise
            
            # Detect FPS if not provided
            if fps is None:
                fps = WebPConverter.detect_fps(input_file)
            
            # For non-animated WebP, create a simple video with the same frame repeated
            if not is_animated:
                # Save the image as a single frame
                frame_file_name = os.path.join(temp_dir, f'{os.path.splitext(os.path.basename(input_file))[0]}-0.png')
                with Image.open(input_file) as img:
                    img.convert('RGBA').save(frame_file_name, 'PNG')
                
                # Create a video with the single frame repeated
                if status_callback:
                    status_callback(f"Creating video from static image")
                clip = ImageSequenceClip([frame_file_name], fps=fps)
                # Make the clip 3 seconds long by repeating the frame
                clip = clip.set_duration(3)
                
                if status_callback:
                    status_callback(f"Encoding video to {os.path.basename(output_file)}")
                clip.write_videofile(output_file, codec='libx264')
                
                if status_callback:
                    status_callback(f"Video created successfully: {os.path.basename(output_file)}")
                return output_file
            
            # For animated WebP, extract all frames
            images = WebPConverter.process_image(input_file, temp_dir, status_callback)
            
            if not images:
                raise ValueError("No frames were extracted from the WebP file")
            
            if status_callback:
                status_callback(f"Creating video from {len(images)} frames")
            clip = ImageSequenceClip(images, fps=fps)
            
            if status_callback:
                status_callback(f"Encoding video to {os.path.basename(output_file)}")
            clip.write_videofile(output_file, codec='libx264')
            
            if status_callback:
                status_callback(f"Video created successfully: {os.path.basename(output_file)}")
            
            return output_file
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
        finally:
            shutil.rmtree(temp_dir)
