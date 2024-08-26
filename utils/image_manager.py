import shutil
import piexif
import os
from PIL import Image
from datetime import datetime


# Constants
Copyright = "Bernard Realino"  # Add name of copyright holder
Artist = "Bernard Realino"  # Add name of artist

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
    total_item = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
            total_item += 1
    return f"Folder selected, {total_item} total items {round(total_size / (1024 * 1024 * 1024), 2)} GB" # Convert to Megabytes

def compress_image(imagefiles, quality, callback):
    log_messages = []
    storage_saved = 0
    total_files = len(imagefiles)
    # st.write(f"Total files: {total_files}")
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
            callback(f"Original: {original_file_size:.2f} MB, Compressed: {compressed_file_size:.2f} MB ({file_name})")
            log_messages.append(f"Processed: {file_name} (Original: {original_file_size:.2f} MB, Compressed: {compressed_file_size:.2f} MB)")
        except IOError:
            file_name = os.path.basename(image_path)
            log_messages.append(f"Error processing: {file_name}")
    
    return log_messages, storage_saved

def organize_by_creation_date_and_type(directory):
    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return
    
    # Define photo and video file extensions, including RAW formats
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                        '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.sr2', '.raf', '.rw2', '.heic'}
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
