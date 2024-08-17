import shutil
import time
import piexif
import os
from PIL import Image
import streamlit as st
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

# Constants
Copyright = "Bernard Realino"  # Add name of copyright holder
Artist = "Bernard Realino"  # Add name of artist

# Helper Functions
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

def compress_image(imagefiles, quality):
    log_messages = []
    storage_saved = 0
    total_files = len(imagefiles)
    st.write(f"Total files: {total_files}")
    for count, image_path in enumerate(imagefiles, start=1):
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
            log_messages.append(f"Processed: {file_name} (Original: {original_file_size:.2f} MB, Compressed: {compressed_file_size:.2f} MB)")
        except IOError:
            file_name = os.path.basename(image_path)
            log_messages.append(f"Error processing: {file_name}")

        # Progress update
        fname, tcount = st.columns(2)
        with fname:
            st.text(file_name)
        with tcount:
            st.text(f"{str(count)}/{str(total_files)}")
        # st.progress(count / total_files)
    
    return log_messages, storage_saved

def organize_by_creation_date_and_type(directory):
    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return
    
    # Define photo and video file extensions, including RAW formats
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                        '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.sr2', '.raf', '.rw2'}
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm'}

    # Iterate through all files in the directory
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Get the creation time and format it as YYYY-MM-DD
        creation_time = os.path.getctime(file_path)
        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y_%m_%d')

        # Determine the file type
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext in photo_extensions:
            subfolder = 'Photos'
        elif file_ext in video_extensions:
            subfolder = 'Videos'
        else:
            continue  # Skip files that are neither photos nor videos

        # Create a new folder with the creation date as the name if it doesn't exist
        new_folder_path = os.path.join(directory, creation_date, subfolder)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        
        # Move the file into the new folder
        shutil.move(file_path, os.path.join(new_folder_path, filename))

    st.success(f"Files have been organized by creation date in {directory}.")

# Streamlit App
st.title("Photo Manager")
st.text("by Bernard Realino")

# Directory Selection
folder_path = st.text_input("Enter the directory path:")

# Compression Quality Selection
quality = st.slider("Compression Quality", min_value=0, max_value=100, value=70)

col1, col2 = st.columns(2)

with col1:
    # Compress Images
    if st.button("Compress Images"):
        if not folder_path:
            st.error("Please select a directory.")
        else:
            original_size = get_folder_size(folder_path)
            image_files = get_all_images(folder_path)
            st.write(f"Original Folder Size: {original_size:.2f} MB")
            
            if not image_files:
                st.error("No image files found in the selected directory.")
            else:
                st.text(f"Compression started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                log_messages, storage_saved = compress_image(image_files, quality)

                compressed_size = get_folder_size(folder_path)

                st.success("Image compression completed.")
                st.write(f"Original Folder Size: {original_size:.2f} MB")
                st.write(f"Compressed Folder Size: {compressed_size:.2f} MB")
                st.write(f"Storage Saved: {storage_saved:.2f} MB")

with col2:
    if st.button("Organize Folder"):
        if not folder_path:
            st.error("Please select a directory")
        else:
            organize_by_creation_date_and_type(folder_path)