import numpy as np
# import cupy as cp
from PIL import Image
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import shutil
from tqdm import tqdm
import yaml

Config = None

def load_config(file_path):
    global Config
    with open(file_path, 'r') as f:
        Config = yaml.safe_load(f)["Compare"]

def get_roi_params():
    roi = np.array(Image.open(Config["ROI_Path"]))
    mask = (roi != [0, 0, 0]).any(axis=2)
    y, x = np.where(mask)
    if len(x) == 0 or len(y) == 0:
        return None, None
    
    x1, x2 = x.min(), x.max()
    y1, y2 = y.min(), y.max()
    w = x2 - x1
    h = y2 - y1
    
    roi_area = roi[y1:y2+1, x1:x2+1]
    avg_color = np.mean(roi_area, axis=(0,1)).astype(int)
    
    return (x1, y1, w, h), avg_color

def check_match(data, roi_params, avg_color, tolerance=30):
    if roi_params is None or avg_color is None:
        return False
    
    x, y, w, h = roi_params
    height, width = 720, 1280
    
    # Calculate number of sections
    sections_y = data.shape[0] // height
    sections_x = data.shape[1] // width
    
    for i in range(sections_y):
        for j in range(sections_x):
            # Extract section
            section = data[i*height:(i+1)*height, j*width:(j+1)*width]
            if y+h <= section.shape[0] and x+w <= section.shape[1]:
                # Extract ROI from section
                roi = section[y:y+h, x:x+w]
                # Calculate average color of ROI using numpy instead of cupy
                roi_avg = np.mean(roi, axis=(0,1)).astype(np.int32)
                # Check if colors match within tolerance
                if np.all(np.abs(roi_avg - avg_color) <= tolerance):
                    return True
    
    return False

def test():
    # Get ROI parameters and average color
    roi_params, avg_color = get_roi_params()
    if roi_params is None:
        print("Error: Could not find ROI")
        return

    # Create output directories if they don't exist
    os.makedirs("Dataset/Positive", exist_ok=True)
    os.makedirs("Dataset/Negative", exist_ok=True)
    os.makedirs("Wrong/False_Pos", exist_ok=True)
    os.makedirs("Wrong/False_Neg", exist_ok=True)

    # Process Negative dataset
    neg_path = "Dataset/Negative"
    for img_name in os.listdir(neg_path):
        if not img_name.endswith(('.png', '.jpg', '.jpeg')):
            continue
        img_path = os.path.join(neg_path, img_name)
        # Use numpy array directly instead of converting to cupy
        img_data = np.array(Image.open(img_path))
        
        if check_match(img_data, roi_params, avg_color):
            print(f"False Positive: {img_name}")
            os.rename(img_path, os.path.join("Wrong/False_Pos", img_name))

    # Process Positive dataset
    pos_path = "Dataset/Positive"
    for img_name in os.listdir(pos_path):
        if not img_name.endswith(('.png', '.jpg', '.jpeg')):
            continue
        img_path = os.path.join(pos_path, img_name)
        # Use numpy array directly instead of converting to cupy
        img_data = np.array(Image.open(img_path))
        
        if not check_match(img_data, roi_params, avg_color):
            print(f"False Negative: {img_name}")
            shutil.copy2(img_path, os.path.join("Wrong/False_Neg", img_name))

def run():
# Get ROI parameters and average color
    roi_params, avg_color = get_roi_params()
    if roi_params is None:
        print("Error: Could not find ROI")
        return

    # Create output directories
    os.makedirs(Config["output_pos"], exist_ok=True)
    os.makedirs(Config["output_neg"], exist_ok=True)

    # Process TODO directory
    todo_path = Config["input"]
    image_files = [f for f in os.listdir(todo_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def process_image(img_name):
        img_path = os.path.join(todo_path, img_name)
        img_data = np.array(Image.open(img_path))
        
        if check_match(img_data, roi_params, avg_color):
            dest = os.path.join(Config["output_pos"], img_name)
        else:
            dest = os.path.join(Config["output_neg"], img_name)
        shutil.move(img_path, dest)

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        list(tqdm(
            executor.map(process_image, image_files),
            total=len(image_files),
            desc="Processing images",
            unit="img"
        ))

if __name__ == "__main__":
    load_config("config.yaml")
    run()