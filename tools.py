import numpy as np
from PIL import Image
import yaml
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import shutil

def cutting():
    config = yaml.safe_load(open("config.yaml", "r"))["Cutting"]
    input_dir = config["input"]
    output_dir = config["output"]

    for file in os.listdir(input_dir):
        if not file.endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        img = Image.open(os.path.join(input_dir, file))
        img_array = np.array(img)
        
        # Find non-black pixels
        non_black = np.any(img_array != [0, 0, 0], axis=2)
        rows = np.any(non_black, axis=1)
        cols = np.any(non_black, axis=0)
        
        # Get boundaries
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        # Crop image
        cropped = img.crop((x_min, y_min, x_max + 1, y_max + 1))
        
        # Save cropped image
        output_path = os.path.join(output_dir, file)
        cropped.save(output_path)

def keep_drop():
    def process_image(file, input_dir, output_dir):
        img = Image.open(os.path.join(input_dir, file))
        width, height = img.size
        
        # Calculate frame dimensions
        frame_width = 1280
        frame_height = 720
        
        # Skip if image is too small for two frames
        if height < frame_height * 2:
            return
        
        # Calculate top position for second frame
        left = 0
        top = min(height - frame_height, frame_height)
        right = min(frame_width, width)
        bottom = min(top + frame_height, height)
        
        # Crop to second frame
        cropped = img.crop((left, top, right, bottom))
        
        # Save cropped image in output directory
        cropped.save(os.path.join(output_dir, file))
    config = yaml.safe_load(open("config.yaml", "r"))["Keep-Drop"]
    input_dir = config["input"]
    output_dir = config["output"]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get list of valid image files
    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        process_func = partial(process_image, input_dir=input_dir, output_dir=output_dir)
        list(tqdm(executor.map(process_func, image_files), total=len(image_files), desc="Processing images"))

def invert():
    config = yaml.safe_load(open("config.yaml", "r"))["Invert"]
    input_dir = config["input"]
    output_dir = config["output"]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def process_image(file):
        img = Image.open(os.path.join(input_dir, file))
        inverted = Image.fromarray(255 - np.array(img))
        inverted.save(os.path.join(output_dir, file))

    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        process_func = partial(process_image)
        list(tqdm(executor.map(process_func, image_files), total=len(image_files), desc="Inverting images"))
        
def rotate_channels():
    config = yaml.safe_load(open("config.yaml", "r"))["Invert"]
    input_dir = config["input"]
    output_dir = config["output"]
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def process_image(file):
        img = Image.open(os.path.join(input_dir, file))
        img_array = np.array(img)
        # Rotate RGB channels to BRG
        rotated = img_array[:, :, [2,1,0]]
        Image.fromarray(rotated).save(os.path.join(output_dir, file))

    image_files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        process_func = partial(process_image)
        list(tqdm(executor.map(process_func, image_files), total=len(image_files), desc="Rotating channels"))


def move_png_files(source_dir='commission', target_dir='TODO'):
    print(f"Moving PNG files from {source_dir} to {target_dir}")
    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Collect all PNG files first
    png_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append((root, file))
    
    # Process files with progress bar
    for root, file in tqdm(png_files, desc="Moving PNG files"):
        source_file = os.path.join(root, file)
        dest_file = os.path.join(target_dir, file)
        
        # Handle duplicate filenames by adding numbers
        counter = 1
        while os.path.exists(dest_file):
            base_name = os.path.splitext(file)[0]
            dest_file = os.path.join(target_dir, f"{base_name}_{counter}.png")
            counter += 1
        
        # Move the file
        shutil.move(source_file, dest_file)
        
def copy_png_files(source_dir='commission', target_dir='TODO'):
    print("Copying PNG files from", source_dir, "to", target_dir)
    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    
    # Collect all PNG files first
    png_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.lower().endswith('.png'):
                png_files.append((root, file))
    
    # Process files with progress bar
    for root, file in tqdm(png_files, desc="Copying PNG files"):
        source_file = os.path.join(root, file)
        dest_file = os.path.join(target_dir, file)
        
        # Handle duplicate filenames by adding numbers
        counter = 1
        while os.path.exists(dest_file):
            base_name = os.path.splitext(file)[0]
            dest_file = os.path.join(target_dir, f"{base_name}_{counter}.png")
            counter += 1
        
        # Copy the file
        shutil.copy2(source_file, dest_file)

def remove_directory(directory_path):
    try:
        shutil.rmtree(directory_path)
    except FileNotFoundError:
        pass
    except PermissionError:
        raise PermissionError(f"Permission denied when trying to remove {directory_path}")

if __name__ == '__main__':
    rotate_channels()