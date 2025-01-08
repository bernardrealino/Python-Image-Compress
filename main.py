import shutil
import piexif
import os
from PIL import Image
import flet as ft
from datetime import datetime

Copyright = "Bernard Realino"
Artist = "Bernard Realino"
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
    return round(total_size / (1024 * 1024), 2)  # Convert to Megabytes

def compress_image(imagefiles, progress_bar, log, original_folder_size, compressed_folder_size, storage_saved_label, file_count_label, quality, create_new_folder):
    file_count = len(imagefiles)
    count = 0
    storage_saved = 0
    new_folder_path = None

    if create_new_folder:
        new_folder_path = os.path.join(directory.value, "Compressed")
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

    for image_path in imagefiles:
        log_message = ""
        try:
            original_file_size = os.path.getsize(image_path) / (1024 * 1024)  # MB
            im = Image.open(image_path)
            try:
                exif_dict = modify_exif(piexif.load(im.info["exif"]))
                exif_bytes = piexif.dump(exif_dict)
            except KeyError:
                exif_bytes = None

            # Determine save path
            if create_new_folder:
                # Create a new folder at the same level as the original folder
                original_parent = os.path.dirname(image_path)
                new_folder_name = os.path.basename(original_parent) + "_Compressed"
                new_folder_path = os.path.join(original_parent, "..", new_folder_name)
                new_folder_path = os.path.abspath(new_folder_path)  # Normalize the path
                if not os.path.exists(new_folder_path):
                    os.makedirs(new_folder_path)
                save_path = os.path.join(new_folder_path, os.path.basename(image_path))
            else:
                save_path = image_path

            if exif_bytes is None:
                im.save(save_path, "jpeg", quality=quality)
            else:
                im.save(save_path, "jpeg", exif=exif_bytes, quality=quality)

            compressed_file_size = os.path.getsize(save_path) / (1024 * 1024)  # MB
            storage_saved += original_file_size - compressed_file_size

            file_name = os.path.basename(image_path)
            log_message = f"From: {original_file_size:.2f} MB\tTo: {compressed_file_size:.2f} MB\t{file_name}\n"
        except IOError:
            file_name = os.path.basename(image_path)
            log_message = f"Error processing: {file_name}\n"
        finally:
            count += 1
            progress_bar.value = (count / file_count)
            progress_bar.update()
            file_count_label.value = f"File {count}/{file_count}"
            file_count_label.update()
            log.value += log_message
            log.update()

    log.value += "\nImage compression completed."
    log.value += f"\nStorage Saved: {storage_saved:.2f} MB"
    log.update()

    # Calculate compressed folder size
    if create_new_folder:
        compressed_size = get_folder_size(new_folder_path)
    else:
        compressed_size = get_folder_size(directory.value)

    compressed_folder_size.value = f"{compressed_size:.2f} MB"
    compressed_folder_size.update()

    storage_saved_label.value = f"Storage Saved: {storage_saved:.2f} MB"
    storage_saved_label.update()
def browse_directory(e):
    folder_path = e.files[0].path.rsplit("\\", 1)[0] + "\\"
    directory.value = folder_path
    directory.update()
    original_size = get_folder_size(folder_path)
    original_size_label.value = f"{original_size:.2f} MB"

    # Update the file count label
    image_files = get_all_images(folder_path)
    file_count_label.value = f"File Count: {len(image_files)}"
    file_count_label.update()

def compress_images(e):
    folder_path = directory.value
    if not folder_path:
        directory.error_text = "Please select a directory."
        directory.update()
        return

    original_size = get_folder_size(folder_path)
    original_size_label.value = f"{original_size} MB"
    original_size_label.update()
    image_files = get_all_images(folder_path)

    if not image_files:
        log.value = "No image files found in the selected directory.\n"
        log.update()
        return

    quality_value = int(quality_slider.value)
    create_new_folder = create_new_folder_checkbox.value

    compressed_folder_size.value = "0.00 MB"
    progress_bar.value = 0
    log.value = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    storage_saved_label.value = "Storage Saved: -"
    file_count_label.value = "File 0/0"
    compress_image(image_files, progress_bar, log, original_size, compressed_folder_size, storage_saved_label, file_count_label, quality_value, create_new_folder)

def organize_by_creation_date_and_type(e):
    # Ensure the folder_path exists
    folder_path = directory.value
    if not os.path.exists(folder_path):
        print(f"Directory {folder_path} does not exist.")
        return
    
    # Define photo and video file extensions, including RAW formats
    photo_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
                        '.cr2', '.cr3', '.nef', '.arw', '.dng', '.orf', '.sr2', '.raf', '.rw2', '.heic'}
    video_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.flv', '.wmv', '.webm'}

    # Iterate through all files in the folder_path
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip directories
        if os.path.isdir(file_path):
            continue
        
        # Get the creation time and format it as YYYY-MM-DD
        creation_time = os.path.getmtime(file_path)
        creation_date = datetime.fromtimestamp(creation_time).strftime('%Y_%m_%d')
        print(creation_date)
        # Determine the file type
        file_ext = os.path.splitext(filename)[1].lower()

        if file_ext in photo_extensions:
            subfolder = 'Photos'
        elif file_ext in video_extensions:
            subfolder = 'Videos'
        else:
            continue  # Skip files that are neither photos nor videos

        # Create a new folder with the creation date as the name if it doesn't exist
        new_folder_path = os.path.join(folder_path, creation_date, subfolder)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        
        # Move the file into the new folder
        shutil.move(file_path, os.path.join(new_folder_path, filename))

        log.value += f"Moved to {creation_date}/{subfolder} - {filename} \n"
        log.update()

def clear_log_button(e):
    log.value=""
    log.update()


def main(page: ft.Page):
    global directory, progress_bar, log, original_size_label, compressed_folder_size, storage_saved_label, file_count_label, quality_slider, create_new_folder_checkbox

    page.title = "Image Compression App"
    page.window_width = 750
    page.theme_mode = ft.ThemeMode.DARK

    copyright_text = ft.Text("bernardrealino.com")
    file_browser = ft.FilePicker(on_result=browse_directory)
    # directory = ft.TextField(value="D:/working/My Project/Python/Projects/Python-Image-Compress/Pictures/Original", label="Directory", multiline=True, expand=True)
    directory = ft.TextField(value="", label="Directory", multiline=True, expand=True)
    # directory = ft.TextField(value="", label="Directory", multiline=True, expand=True)
    browse_button = ft.ElevatedButton(text="Browse", on_click=lambda _: file_browser.pick_files())
    
    quality_slider = ft.Slider(width = 530, min=0, max=100, value=quality, divisions=10, label="{value}%", on_change=lambda e: e.control.update())
    compress_button = ft.ElevatedButton(text="Compress Images", on_click=compress_images)
    organize_button = ft.ElevatedButton(text="Organize", on_click=organize_by_creation_date_and_type)
    create_new_folder_checkbox = ft.Checkbox(label="Save in a new folder", value=True)
    
    original_size_label = ft.Text(value="0.00 MB", size=50)
    compressed_folder_size = ft.Text(value="0.00 MB", size=50)
    file_count_label = ft.Text(value="File 0/0")
    
    original_size_card = ft.Card(ft.Column([ft.Text("Original Folder Size (MB):"), original_size_label], horizontal_alignment=ft.CrossAxisAlignment.CENTER,))
    compressed_size_card = ft.Card(ft.Column([ft.Text("Compressed Folder Size:"), compressed_folder_size], horizontal_alignment=ft.CrossAxisAlignment.CENTER,))


    progress_bar = ft.ProgressBar(width=600, value=0)
    clear_log = ft.ElevatedButton("Clear Log", on_click=clear_log_button)
    log = ft.TextField(value="", label="Log", multiline=True, max_lines=10)
    storage_saved_label = ft.Text(value="Storage Saved: -")

    page.controls.append(file_browser)
    page.scroll = True
    page.add(
        ft.Column([
            ft.Row([directory, browse_button]),
            ft.Row([ft.Text("Compression Quality:"), quality_slider]),
            
            ft.Row([compress_button, organize_button, create_new_folder_checkbox]),
            ft.Row([original_size_card, compressed_size_card], alignment=ft.MainAxisAlignment.SPACE_AROUND),
            ft.Row([progress_bar, file_count_label]),
            clear_log,
            log,
            copyright_text,
        ])
    )

ft.app(target=main)
