import os
import tkinter as tk
from tkinter import filedialog, Tk, Canvas, Button
from PIL import Image, ImageTk
import subprocess
import time
import shutil
import filecmp
from filecmp import cmp

class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector App")
        self.image_path = None
        self.temp_folder = 'temp'
        self.temp_images = []

        # Canvas to display the image
        self.canvas = tk.Canvas(root, bg="white", cursor="cross")
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # "Save Selection" button
        self.save_button = tk.Button(root, text="Save Selection", command=self.on_button_release)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

        # "Remove temp files" button
        self.save_button = tk.Button(root, text="Remove temp files", command=self.remove_all_folders)
        self.save_button.pack(side=tk.LEFT, padx=10, pady=10)

        # "Run Another Program" button
        self.run_button = tk.Button(root, text="Run Another Program", command=self.run_another_program)
        self.run_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # "Load Image" button
        self.load_button = tk.Button(root, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.RIGHT, padx=10, pady=10)

        # Create a PhotoImage object
        self.photo = tk.PhotoImage()

        self.selected_portions = []
        self.selection_coordinates = {}

    def remove_all_folders(self):
        folder = 'temp'
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def remove_duplicate_images(self):
        temp_folder_contents = os.listdir(self.temp_folder)

        for i, img_path1 in enumerate(temp_folder_contents):
            for j, img_path2 in enumerate(temp_folder_contents[i+1:]):
                full_path1 = os.path.join(self.temp_folder, img_path1)
                full_path2 = os.path.join(self.temp_folder, temp_folder_contents[j+i+1])

                if filecmp.cmp(full_path1, full_path2):
                    os.remove(full_path2)
                    if full_path2 in self.selected_portions:
                        self.selected_portions.remove(full_path2)

    def print_selection_coordinates(self):
        print("Selection Coordinates:")
        for selection, coordinates in self.selection_coordinates.items():
            print(f"{selection}: {coordinates}")

    def load_image(self):
        file_path = filedialog.askopenfilename()

        if file_path:
            self.image_path = file_path
            original_image = Image.open(file_path)

            # Scale down the image by 1/3
            scale_factor = 1/3
            new_width = int(original_image.width * scale_factor)
            new_height = int(original_image.height * scale_factor)
            resized_image = original_image.resize((new_width, new_height), Image.BILINEAR)

            # Update the PhotoImage object
            self.photo = ImageTk.PhotoImage(resized_image)
            self.canvas.config(scrollregion=(0, 0, new_width, new_height))
            self.canvas.delete("all")  # Clear canvas content

            # Display the resized image on the canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo, tags="image")

            self.selected_portions = []

    def run_another_program(self):
        # Specify the path to your Python script
        script_path = 'main.py'

        try:
            # Run the specified Python script using subprocess
            subprocess.run(['python', script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running the script: {e}")
    def on_button_press(self, event):
        # Record the starting coordinates when the mouse button is pressed
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # Delete any existing selection rectangle
        self.canvas.delete("selection_rectangle")

    def on_mouse_drag(self, event):
        # Update the coordinates as the mouse is dragged
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        # Delete any existing selection rectangle
        self.canvas.delete("selection_rectangle")

        # Draw a new selection rectangle
        self.selection_rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y, outline="red", tags="selection_rectangle"
        )

    def on_button_release(self, event=None):
        if self.image_path and hasattr(self, 'selection_rectangle'):
            # Coordinates of the selection rectangle on the canvas
            x1, y1, x2, y2 = self.canvas.coords(self.selection_rectangle)

            # Convert coordinates to image coordinates on the scaled-down image
            scale_factor = 1/3  # Assuming the image was scaled down by 1/3
            x1_img_scaled = max(0, int(x1 / scale_factor))
            y1_img_scaled = max(0, int(y1 / scale_factor))
            x2_img_scaled = min(self.photo.width() / scale_factor, int(x2 / scale_factor))
            y2_img_scaled = min(self.photo.height() / scale_factor, int(y2 / scale_factor))

            # Get the selected region from the original image
            image = Image.open(self.image_path)
            region_scaled = (x1_img_scaled, y1_img_scaled, x2_img_scaled, y2_img_scaled)

            try:
                cropped_image_scaled = image.crop(region_scaled)
            except ValueError:
                # Handle the case where the coordinates are not valid
                return

            # Save the selected portion with a unique filename
            count = len(self.selected_portions) + 1
            temp_image_path = os.path.join(self.temp_folder, f'selection_{count}.png')

            cropped_image_scaled.save(temp_image_path)

            coordinates = (x1, y1, x2, y2)
            self.selection_coordinates[os.path.basename(temp_image_path)] = coordinates

            # Draw a new persistent selection rectangle
            persistent_rectangle = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", tags="selection_rectangle_persistent")

            # Display the persistent rectangle
            self.canvas.itemconfig(persistent_rectangle, tags="selection_rectangle_persistent")

            # Keep track of the selected portion
            self.selected_portions.append(temp_image_path)

            # Keep track of the selected portion
            self.remove_duplicate_images()

            # Add text label above the rectangle with the filename
            label_text = f'selection_{count}.png'
            label = self.canvas.create_text((x1 + x2) / 2, y1, text=label_text, anchor="s", font=("Helvetica", 8))

            # Keep a reference to the label to avoid it being garbage collected
            self.canvas.itemconfig(persistent_rectangle, tags=("selection_rectangle_persistent", label))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
