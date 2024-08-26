import flet as ft

from components.select_folder import select_folder
from utils.image_manager import compress_image, get_all_images

def main(page: ft.Page):
    page.title = "test"
    page.window.height = 500
    page.window.width = 800

    folder_selected = ""

    def on_compressed_image(image):
        page.controls.append(
           
            ft.Container(
                content= ft.Text(f"{image} compressed"),
                bgcolor=ft.colors.GREEN_900,        # Background color
                padding=10,            # Optional: Add padding around the text
                border_radius=10,      # Rounded corners (10px radius)
            )
        )
        page.update() 

    def on_folder_selected(path):
        global folder_selected
        folder_selected = path
        print(folder_selected)
        page.controls.append(ft.Text("Choose Quality"))
        quality_slider = ft.Slider(min=0, max=100, divisions=10, value=30, label="{value}%")
        page.controls.append(quality_slider)
        page.controls.append(ft.ElevatedButton("Compress", on_click=lambda _, folder_selected=folder_selected:compress_image(get_all_images(folder_selected), int(quality_slider.value), on_compressed_image)))
        page.update()

    completed_listview = ft.ListView()
    page.controls.append(completed_listview)
    page.controls.append(select_folder(page, on_folder_selected))
    page.scroll=True
    page.update()

if __name__ == "__main__":
    ft.app(main)