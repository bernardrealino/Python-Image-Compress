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

def compress_image(imagefiles, progress_bar, log, original_folder_size, compressed_folder_size, storage_saved_label, file_count_label, quality):
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
            log_message = f"From: {original_file_size:.2f} MB\t"
            log_message += f"To: {compressed_file_size:.2f} MB\t"
            log_message += f"{file_name}\n"
        except IOError:
            file_name = os.path.basename(image_path)
            log_message = f"Error processing: {file_name}\n"
        finally:
            count += 1
            progress_bar.value = (count / file_count)
            progress_bar.update()
            file_count_label.value = f"File {count}/{file_count}"  # Update current file number
            file_count_label.update()
            log.value += log_message
            log.update()

    log.value += "\nImage compression completed."
    log.value += f"\nStorage Saved: {storage_saved:.2f} MB"
    log.update()

    # Calculate compressed folder size in Megabytes
    compressed_size = get_folder_size(directory.value)
    compressed_folder_size.value = f"{compressed_size:.2f} MB"  # Shorter compressed folder size
    compressed_folder_size.update()

    # Calculate and display storage saved
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

    quality_value = int(quality_slider.value)  # Get the quality from the slider

    compressed_folder_size.value = "0.00 MB"
    progress_bar.value = 0
    log.value = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    storage_saved_label.value = "Storage Saved: -"
    file_count_label.value = "File 0/0"  # Initialize file count label
    compress_image(image_files, progress_bar, log, original_size, compressed_folder_size, storage_saved_label, file_count_label, quality_value)

def main(page: ft.Page):
    global directory, progress_bar, log, original_size_label, compressed_folder_size, storage_saved_label, file_count_label, quality_slider

    page.title = "Image Compression App"
    page.window.width = 700
    page.theme_mode = ft.ThemeMode.DARK

    copyright_text = ft.Text("bernardrealino.com")
    file_browser = ft.FilePicker(on_result=browse_directory)
    directory = ft.TextField(value="D:/working/My Project/Python/Projects/Python-Image-Compress/Pictures/Original", label="Directory", multiline=True, expand=True)
    # directory = ft.TextField(value="", label="Directory", multiline=True, expand=True)
    browse_button = ft.ElevatedButton(text="Browse", on_click=lambda _: file_browser.pick_files())
    
    quality_slider = ft.Slider(width = 530, min=0, max=100, value=quality, divisions=10, label="{value}%", on_change=lambda e: e.control.update())
    compress_button = ft.ElevatedButton(text="Compress Images", on_click=compress_images)
    
    original_size_label = ft.Text(value="0.00 MB")
    compressed_folder_size = ft.Text(value="0.00 MB")
    file_count_label = ft.Text(value="File 0/0")
    
    progress_bar = ft.ProgressBar(width=600, value=0)
    log = ft.TextField(value="", label="Log", multiline=True)
    storage_saved_label = ft.Text(value="Storage Saved: -")

    page.controls.append(file_browser)
    page.scroll = True
    page.add(
        ft.Column([
            ft.Row([directory, browse_button]),
            ft.Row([ft.Text("Compression Quality:"), quality_slider]),
            ft.Row([compress_button, ft.Text("Original Folder Size (MB):"), original_size_label, ft.Text("Compressed Folder Size:"), compressed_folder_size]),
            ft.Row([progress_bar, file_count_label]),
            # storage_saved_label,
            log,
            copyright_text,
        ])
    )

ft.app(target=main)
