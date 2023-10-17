import piexif
import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime

Copyright = "Bernard Realino"  # add name of copyright holder
Artist = "Bernard Realino"  # add name of artist
quality = 70

def get_all_images(root):
    valid_format = ['JPG', 'JPEG']
    response = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            extension = name.split('.')[-1:][0].upper()
            if extension in valid_format:
                response.append(os.path.join(path, name))
    return response

def modify_exif(exif_dict):
    global Copyright, Artist

    if exif_dict != 0:
        exif_dict['0th'][piexif.ImageIFD.Copyright] = Copyright
        exif_dict['0th'][piexif.ImageIFD.Artist] = Artist

    return exif_dict

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size / (1024 * 1024)  # Convert to Megabytes

def compress_image(imagefiles, progress_bar, log_text, original_folder_size, compressed_folder_size, storage_saved_label, file_count_label, quality):
    file_count = len(imagefiles)
    count = 0
    storage_saved = 0  # Initialize storage saved
    for image_path in imagefiles:
        log_message = ""  # Initialize log_message
        try:
            original_file_size = os.path.getsize(image_path) / (1024 * 1024)  # Convert to Megabytes
            im = Image.open(image_path)
            try:
                exif_dict = modify_exif(piexif.load(im.info["exif"]))
                exif_bytes = piexif.dump(exif_dict)
            except KeyError:
                exif_bytes = None

            if exif_bytes is None:
                im.save(image_path, "jpeg", quality=quality)
            else:
                im.save(image_path, "jpeg", exif=exif_bytes, quality=quality)
            
            compressed_file_size = os.path.getsize(image_path) / (1024 * 1024)  # Convert to Megabytes
            storage_saved += original_file_size - compressed_file_size  # Calculate storage saved

            file_name = os.path.basename(image_path)
            log_message = f"Processed: {file_name}\n"
            log_message += f"\tOriginal Size: {original_file_size:.2f} MB\n"
            log_message += f"\tCompressed Size: {compressed_file_size:.2f} MB\n"
        except IOError:
            file_name = os.path.basename(image_path)
            log_message = f"Error processing: {file_name}\n"
        finally:
            count += 1
            progress = (count / file_count) * 100
            progress_bar["value"] = progress
            file_count_label.config(text=f"File {count}/{file_count}")  # Update current file number
            app.update_idletasks()
            log_text.insert(tk.END, log_message)
            log_text.see(tk.END)

    log_text.insert(tk.END, "Image compression completed.\n")
    log_text.see(tk.END)

    # Calculate compressed folder size in Megabytes
    compressed_size = get_folder_size(directory_entry.get())
    compressed_folder_size.set(f"{compressed_size:.2f} MB")  # Shorter compressed folder size

    # Calculate and display storage saved
    storage_saved_label.config(text=f"Storage Saved: {storage_saved:.2f} MB")

def browse_directory():
    folder_path = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, folder_path)

    # Update the original folder size immediately
    original_size = get_folder_size(folder_path)
    original_size_label.config(text=f"{original_size:.2f} MB")

    # Update the file count label
    image_files = get_all_images(folder_path)
    file_count_label.config(text=f"File Count: {len(image_files)}")  # Define the file_count_label

def compress_images():
    folder_path = directory_entry.get()
    if not folder_path:
        messagebox.showerror("Error", "Please select a directory.")
        return

    original_size = get_folder_size(folder_path)

    image_files = get_all_images(folder_path)

    if not image_files:
        messagebox.showerror("Error", "No image files found in the selected directory.")
        return

    quality_value = quality_scale.get()  # Get the quality from the scale

    compressed_folder_size.set(0)
    progress_bar["value"] = 0
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, f"Compression started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    storage_saved_label.config(text="Storage Saved: -")
    file_count_label.config(text="File 0/0")  # Initialize file count label
    compress_image(image_files, progress_bar, log_text, original_size, compressed_folder_size, storage_saved_label, file_count_label, quality_value)

# Create the main application window
app = tk.Tk()
app.title("Image Compression App")

# Create and configure UI elements using the grid layout
# Row 0: Directory selection
directory_label = tk.Label(app, text="Select a directory:")
directory_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
directory_entry = tk.Entry(app)
directory_entry.grid(row=0, column=1, padx=10, pady=10, columnspan=3, sticky='ew')
browse_button = tk.Button(app, text="Browse", command=browse_directory)
browse_button.grid(row=0, column=4, padx=10, pady=10)
# Row 1: Compression quality scale
quality_label = tk.Label(app, text="Compression Quality:")
quality_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')
quality_scale = tk.Scale(app, from_=0, to=100, orient="horizontal")
quality_scale.set(quality)  # Set the default quality
quality_scale.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky='ew')
# Row 2: Compress button and folder size labels
compress_button = tk.Button(app, text="Compress Images", command=compress_images)
compress_button.grid(row=2, column=0, padx=10, pady=10, sticky='w')
original_folder_size_label = tk.Label(app, text="Original Folder Size (MB):")
original_folder_size_label.grid(row=2, column=1, padx=10, pady=10)
original_size_label = tk.Label(app, text="0.00 MB")
original_size_label.grid(row=2, column=2, padx=10, pady=10, sticky='w')
compressed_folder_size_label = tk.Label(app, text="Compressed Folder Size:")
compressed_folder_size_label.grid(row=2, column=3, padx=10, pady=10)
compressed_folder_size = tk.StringVar()
compressed_size_label = tk.Label(app, textvariable=compressed_folder_size)
compressed_size_label.grid(row=2, column=4, padx=10, pady=10, sticky='w')
# Row 3: File Count Label and Progress Bar
file_count_label = tk.Label(app, text="File 0/0")  # Define the file_count_label
file_count_label.grid(row=3, column=0, padx=10, pady=10, sticky='w')  # Position file_count_label
progress_bar = ttk.Progressbar(app, length=600, mode="determinate")
progress_bar.grid(row=3, column=1, columnspan=4, padx=10, pady=10, sticky='w')
# Row 4: Log
log_label = tk.Label(app, text="Log:")
log_label.grid(row=4, column=0, padx=10, pady=10)
log_text = tk.Text(app, wrap=tk.WORD, height=10, width=80)
log_text.grid(row=4, column=1, columnspan=5, padx=10, pady=10)
# Row 5: Storage saved label
storage_saved_label = tk.Label(app, text="Storage Saved: -")
storage_saved_label.grid(row=5, column=0, columnspan=5, padx=10, pady=10)
# Start the application
app.mainloop()
