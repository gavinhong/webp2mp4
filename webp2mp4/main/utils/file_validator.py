"""
File Validator Module
Provides utilities for validating WebP files
"""

import os
from PIL import Image


class FileValidator:
    """
    Utility class for validating files before conversion
    """
    
    @staticmethod
    def validate_webp_files(files):
        """
        Validate that all selected files are WebP files.
        
        Args:
            files (list): List of file paths to validate
            
        Returns:
            tuple: (valid_files, invalid_files) where valid_files is a list of valid WebP file paths
                  and invalid_files is a list of tuples (file_path, reason) for invalid files
        """
        valid_files = []
        invalid_files = []
        
        for file in files:
            try:
                # Check if file exists
                if not os.path.exists(file):
                    invalid_files.append((file, "File does not exist"))
                    continue
                    
                # Try to open with PIL to verify it's a valid image
                with Image.open(file) as img:
                    if img.format != "WEBP":
                        invalid_files.append((file, f"Not a WebP file (detected as {img.format})"))
                    else:
                        valid_files.append(file)
            except Exception as e:
                invalid_files.append((file, f"Error: {str(e)}"))
        
        return valid_files, invalid_files
