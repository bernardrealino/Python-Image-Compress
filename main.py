import piexif
import os
from PIL import Image
import streamlit as st
from datetime import datetime

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
        st.progress(count / total_files)
    
    return log_messages, storage_saved

# Streamlit App
st.title("Image Compression App")

# Directory Selection
folder_path = st.text_input("Enter the directory path:")
if st.button("Browse"):
    folder_path = st.text_input("Enter the directory path:", folder_path)

# Compression Quality Selection
quality = st.slider("Compression Quality", min_value=0, max_value=100, value=70)

# Compress Images
if st.button("Compress Images"):
    if not folder_path:
        st.error("Please select a directory.")
    else:
        original_size = get_folder_size(folder_path)
        image_files = get_all_images(folder_path)
        
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
            st.text_area("Log", value="\n".join(log_messages), height=200)
