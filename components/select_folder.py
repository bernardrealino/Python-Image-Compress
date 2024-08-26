import flet as ft

from utils.image_manager import get_folder_size

def select_folder(page, callback):
    def on_filepicker_result(e: ft.FilePickerResultEvent):
        file_browser_textarea.value = e.files[0].path.rsplit("\\", 1)[0] + "\\"
        file_browser_textarea.update()
        folder_browser.controls.append(
                            
                ft.Container(
                    content=ft.Text(get_folder_size(file_browser_textarea.value), style=ft.TextStyle(size=18)),
                    bgcolor=ft.colors.GREEN_900,        # Background color
                    padding=10,            # Optional: Add padding around the text
                    border_radius=10,      # Rounded corners (10px radius)
                )
            )
        folder_browser.update()
        callback(file_browser_textarea.value)

    file_browser = ft.FilePicker(on_result=on_filepicker_result)
    page.controls.append(file_browser)
    file_browser_textarea = ft.TextField(label="Folder Path")
    file_browser_button = ft.ElevatedButton("Select Folder",on_click=lambda _: file_browser.pick_files(),)
    folder_browser = ft.Column(
        [   
            file_browser_textarea,
            file_browser_button
        ]
    )
    

    return folder_browser