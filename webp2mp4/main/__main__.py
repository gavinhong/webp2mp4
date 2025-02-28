#!/usr/bin/env python3
"""
Main entry point for the WebP to MP4 converter application
"""

import sys
import os
import tkinter as tk

# Add the parent directory to sys.path if running as a script
if __name__ == "__main__" and __package__ is None:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    __package__ = "main"

from main.ui.main_window import MainWindow, TKDND_AVAILABLE

# Try to import tkinterdnd2, but don't fail if it's not available
if TKDND_AVAILABLE:
    from tkinterdnd2 import TkinterDnD


def is_frozen():
    """Check if the application is running as a frozen executable"""
    return getattr(sys, 'frozen', False)


def main():
    """
    Main function to start the application
    """
    try:
        # Create the main window with TkinterDnD if available, otherwise standard tkinter
        if TKDND_AVAILABLE:
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        
        app = MainWindow(root)
        root.mainloop()
    except Exception as e:
        # Only print errors if not running as a frozen executable
        if not is_frozen():
            print(f"Error starting application: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
