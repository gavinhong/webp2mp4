"""
Main window for the WebP to MP4 converter application
"""

import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys

# Try to import tkinterdnd2, but don't fail if it's not available
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TKDND_AVAILABLE = True
except ImportError:
    TKDND_AVAILABLE = False


class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        """
        Initialize the main window
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("WebP to MP4 Converter")
        self.root.geometry("700x720")  # Further increased height to ensure all content is visible
        self.root.minsize(650, 720)    # Increased minimum height as well
        
        self.selected_files = []
        self.setup_ui()
        
        # Set up drag and drop
        self.setup_dnd()
    
    def setup_dnd(self):
        """Set up drag and drop functionality"""
        if TKDND_AVAILABLE:
            # If tkinterdnd2 is available, use it
            self.file_listbox.drop_target_register(DND_FILES)
            self.file_listbox.dnd_bind('<<Drop>>', self.on_drop_files)
            
            # Also register the root window
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop_files)
    
    def on_drop_files(self, event):
        """Handle files dropped onto the widget"""
        # Get the data (file paths)
        data = event.data
        
        # Print debug info
        print(f"Raw drop data: {data}")
        
        # Process the paths based on the format
        file_paths = []
        
        # Handle different formats of dropped data
        if '{' in data and '}' in data:
            # TkinterDnD2 format: {C:/path/to/file} {C:/path/to/another/file}
            # Split by closing brace followed by space and opening brace
            parts = data.split('} {')
            
            # Process first part (may have leading '{')
            first_part = parts[0].lstrip('{')
            if first_part and os.path.exists(first_part):
                file_paths.append(first_part)
            
            # Process middle parts (no braces needed)
            for part in parts[1:-1]:
                if part and os.path.exists(part):
                    file_paths.append(part)
            
            # Process last part (may have trailing '}')
            if len(parts) > 1:
                last_part = parts[-1].rstrip('}')
                if last_part and os.path.exists(last_part):
                    file_paths.append(last_part)
        else:
            # Simple space-separated format
            for path in data.split():
                if path and os.path.exists(path):
                    file_paths.append(path)
        
        print(f"Parsed file paths: {file_paths}")
        
        # Process the files
        if file_paths:
            self._process_selected_files(file_paths)
            # Make sure the listbox is updated
            self.update_file_listbox()
        else:
            messagebox.showwarning("Warning", "No valid files were dropped")
        
        return "break"  # Prevent further processing
    
    def setup_ui(self):
        """Set up the user interface elements"""
        # Frame for file selection
        file_frame = ttk.LabelFrame(self.root, text="File Selection")
        file_frame.pack(fill="both", expand=True, padx=10, pady=2)
        
        # Button to select files
        select_btn = ttk.Button(file_frame, text="Select WebP Files", command=self.select_files)
        select_btn.pack(pady=2)
        
        # Add a label to indicate file selection method - moved below the button
        file_label = ttk.Label(file_frame, text="Use 'Select WebP Files' button to add files", foreground="gray")
        file_label.pack(pady=2)
        
        # Listbox to display selected files
        self.file_listbox = tk.Listbox(file_frame, width=70, height=6)
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=2)
        
        # Add a label to indicate drag and drop is available
        drag_label = ttk.Label(file_frame, text="Drag and drop WebP files here", foreground="gray")
        drag_label.pack(pady=2)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        # Clear selection button
        clear_btn = ttk.Button(file_frame, text="Clear Selection", command=self.clear_selection)
        clear_btn.pack(pady=2)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.root, text="Conversion Options")
        options_frame.pack(fill="both", expand=False, padx=10, pady=2)
        
        # FPS option
        fps_frame = ttk.Frame(options_frame)
        fps_frame.pack(fill="x", padx=10, pady=2)
        
        ttk.Label(fps_frame, text="FPS:").pack(side="left", padx=5)
        self.fps_var = tk.StringVar(value="")  # Empty by default
        fps_entry = ttk.Entry(fps_frame, textvariable=self.fps_var, width=15)
        fps_entry.pack(side="left", padx=5)
        
        # Create a new frame for the FPS tooltip
        fps_tooltip_frame = ttk.Frame(options_frame)
        fps_tooltip_frame.pack(fill="x", padx=10, pady=2)
        
        # Add tooltip for FPS - moved to its own frame below the controls
        fps_tooltip = ttk.Label(fps_tooltip_frame, text="(Leave empty to use original frame rate)", foreground="gray")
        fps_tooltip.pack(side="left", padx=5)
        
        # Output directory option
        out_dir_frame = ttk.Frame(options_frame)
        out_dir_frame.pack(fill="x", padx=10, pady=2)
        
        ttk.Label(out_dir_frame, text="Output Directory:").pack(side="left", padx=5)
        # Default to empty for using original file path
        self.output_var = tk.StringVar(value="")
        out_dir_entry = ttk.Entry(out_dir_frame, textvariable=self.output_var, width=40)
        out_dir_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        browse_btn = ttk.Button(out_dir_frame, text="Browse", command=self.select_output_dir)
        browse_btn.pack(side="left", padx=5)
        
        # Create a new frame for the output directory tooltip
        out_dir_tooltip_frame = ttk.Frame(options_frame)
        out_dir_tooltip_frame.pack(fill="x", padx=10, pady=2)
        
        # Add tooltip for output directory - moved to its own frame below the controls
        out_dir_tooltip = ttk.Label(out_dir_tooltip_frame, text="(Leave empty to save in the same folder as the input file)", foreground="gray")
        out_dir_tooltip.pack(side="left", padx=5)
        
        # Convert button
        convert_btn = ttk.Button(self.root, text="Convert to MP4", command=self.start_conversion)
        convert_btn.pack(pady=2)
        
        # Progress bars frame
        progress_frame = ttk.LabelFrame(self.root, text="Conversion Progress")
        progress_frame.pack(fill="x", padx=10, pady=2)
        
        # Overall progress
        ttk.Label(progress_frame, text="Overall Progress:").pack(anchor="w", padx=10, pady=(10, 0))
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=2)
        
        # Single file progress
        ttk.Label(progress_frame, text="Current File Progress:").pack(anchor="w", padx=10, pady=(10, 0))
        self.file_progress_var = tk.DoubleVar()
        self.file_progress_bar = ttk.Progressbar(progress_frame, variable=self.file_progress_var, maximum=100)
        self.file_progress_bar.pack(fill="x", padx=10, pady=(5, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill="x", padx=10, pady=(5, 15), side="bottom")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, wraplength=650, justify="center")
        status_label.pack(fill="x", pady=2)
    
    def select_files(self):
        """Open a file dialog to select WebP files"""
        files = filedialog.askopenfilenames(
            title="Select WebP Files",
            filetypes=[("WebP files", "*.webp"), ("All files", "*.*")]
        )
        
        if files:
            self._process_selected_files(files)
    
    def _process_selected_files(self, files):
        """
        Process the selected files
        
        Args:
            files: List of file paths
        """
        # Filter for WebP files
        valid_files = [f for f in files if f.lower().endswith('.webp')]
        
        if not valid_files:
            messagebox.showwarning("Warning", "No valid WebP files were selected")
            return
        
        # Check for duplicates and only add new files
        new_files = [f for f in valid_files if f not in self.selected_files]
        
        if new_files:
            # Add valid files to the list
            self.selected_files.extend(new_files)
            # Update the listbox with the new files
            self.update_file_listbox()
            
            # Show a message about how many files were added
            messagebox.showinfo(
                "Files Added", 
                f"{len(new_files)} WebP file(s) added for conversion"
            )
        else:
            # If all files were duplicates
            if len(valid_files) == len(files):
                messagebox.showinfo("Info", "All selected files are already in the list")
            else:
                messagebox.showinfo(
                    "Info", 
                    f"Found {len(valid_files)} WebP file(s), but all are already in the list"
                )
    
    def update_file_listbox(self):
        """Update the listbox with the current selected files"""
        self.file_listbox.delete(0, tk.END)
        for file in self.selected_files:
            self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def clear_selection(self):
        """Clear the selected files list"""
        self.selected_files = []
        self.update_file_listbox()
    
    def select_output_dir(self):
        """Open a directory dialog to select the output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_var.set(directory)
    
    def start_conversion(self):
        """Start the conversion process"""
        if not self.selected_files:
            messagebox.showerror("Error", "No WebP files selected")
            return
        
        # Get FPS value
        fps_text = self.fps_var.get()
        if fps_text == "":
            # Will be determined for each file during conversion
            fps = None
        else:
            try:
                fps = float(fps_text)
                if fps <= 0:
                    messagebox.showerror("Error", "FPS must be a positive number")
                    return
            except ValueError:
                messagebox.showerror("Error", "Invalid FPS value")
                return
        
        # Get output directory
        output_dir = self.output_var.get().strip()
        if output_dir and not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Invalid output directory")
            return
        
        # Disable buttons during conversion
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state="disabled")
        
        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting conversion...")
        
        # Start conversion in a separate thread
        self.conversion_thread = threading.Thread(
            target=self.convert_files,
            args=(self.selected_files, fps, output_dir),
            daemon=True
        )
        self.conversion_thread.start()
    
    def convert_files(self, files, fps, output_dir):
        """Convert the selected files in a separate thread"""
        from main.core.converter import WebPConverter
        
        total_files = len(files)
        converted = 0
        
        for file_path in files:
            try:
                self.status_var.set(f"Converting {os.path.basename(file_path)}...")
                self.file_progress_var.set(0)  # Reset single file progress
                
                # Determine FPS for this file if set to auto
                file_fps = fps
                if file_fps is None:
                    file_fps = WebPConverter.detect_fps(file_path)
                    self.status_var.set(f"Converting {os.path.basename(file_path)} at {file_fps:.2f} FPS...")
                
                # Determine output path
                if output_dir:
                    # Use specified output directory
                    output_path = os.path.join(output_dir, os.path.splitext(os.path.basename(file_path))[0] + ".mp4")
                else:
                    # Use same directory as input file
                    output_path = os.path.splitext(file_path)[0] + ".mp4"
                
                # Convert the file with file progress callback
                WebPConverter.convert(file_path, output_path, file_fps, self.update_status_and_progress)
                
                converted += 1
                self.progress_var.set((converted / total_files) * 100)
                
            except Exception as e:
                self.status_var.set(f"Error converting {os.path.basename(file_path)}: {str(e)}")
                self.file_progress_var.set(0)  # Reset file progress on error
                time.sleep(2)  # Pause to show the error
        
        self.status_var.set(f"Conversion complete. Converted {converted} of {total_files} files.")
        self.file_progress_var.set(0)  # Reset file progress when done
        
        # Re-enable buttons
        self.root.after(0, self.enable_buttons)
    
    def update_status_and_progress(self, status_text):
        """Update both status text and file progress based on status message"""
        self.status_var.set(status_text)
        
        # Try to extract progress information from status text
        try:
            if "Processing frame " in status_text:
                # Extract frame number from status text like "Processing frame 5 of file.webp"
                parts = status_text.split()
                if len(parts) >= 3 and parts[0] == "Processing" and parts[1] == "frame":
                    frame_num = int(parts[2])
                    # We don't know the total frames, but we can update based on what we've seen
                    # Use a simple approach: increment progress as we process more frames
                    progress = min(frame_num, 100)  # Cap at 100%
                    self.file_progress_var.set(progress)
            elif "Creating video" in status_text:
                # When creating the final video, set progress to 90%
                self.file_progress_var.set(90)
            elif "complete" in status_text.lower() or "created successfully" in status_text.lower():
                # When complete, set to 100%
                self.file_progress_var.set(100)
        except Exception:
            # If any error in parsing, don't update progress
            pass
    
    def enable_buttons(self):
        """Re-enable all buttons after conversion is complete"""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state="normal")
