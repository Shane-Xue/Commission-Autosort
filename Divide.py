import yaml
import numpy as np
from PIL import Image
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tqdm import tqdm

config = yaml.safe_load(open("config.yaml", 'r'))["Divide"]

def get_roi_data():
    
    # Load image using PIL
    roi = Image.open(config["ROI_Path"])
    if roi is None:
        raise FileNotFoundError(f"Could not load ROI from {config['ROI_Path']}")
    
    # Convert to numpy array
    roi_array = np.array(roi)
    
    # Create binary mask for non-black pixels
    # Assuming black is [0,0,0]
    non_black = np.any(roi_array > 0, axis=2)
    
    # Find coordinates of non-black pixels
    y_coords, x_coords = np.nonzero(non_black)
    
    if len(x_coords) == 0:
        raise ValueError("No non-black regions found in ROI")
    
    # Calculate bounding box
    x = np.min(x_coords)
    y = np.min(y_coords)
    w = np.max(x_coords) - x + 1
    h = np.max(y_coords) - y + 1
    
    # Calculate average color in the region
    roi_region = roi_array[y:y+h, x:x+w]
    avg_color = np.mean(roi_region, axis=(0,1)).astype(int)
    
    return (x, y, w, h), tuple(avg_color)

def divide_image(image_array, roi, avg_color):
    x, y, w, h = roi
    frame_height = 720
    image_height = image_array.shape[0]
    num_frames = image_height // frame_height
    splits = []
    
    # Create a view of the image as a 4D array (frames, height, width, channels)
    frames = image_array.reshape(num_frames, frame_height, image_array.shape[1], -1)
    current_split = []
    
    for i in range(num_frames):
        frame = frames[i]
        frame_roi = frame[y:y + h, x:x + w]
        frame_avg = np.mean(frame_roi, axis=(0,1)).astype(int)
        
        color_diff = np.abs(frame_avg - avg_color)
        if np.all(color_diff <= 10):
            if current_split:
                splits.append(np.vstack(current_split))
                current_split = []
        current_split.append(frame)
    
    # Don't forget the last split
    if current_split:
        splits.append(np.vstack(current_split))
    
    return splits

def process_single_image(input_path):
    # Get original filename and extension
    filename = Path(input_path).stem
    extension = Path(input_path).suffix
    
    # Load and convert image to numpy array
    img = Image.open(input_path)
    img_array = np.array(img)
    
    # Get ROI data
    roi, avg_color = get_roi_data()
    
    # Divide image
    splits = divide_image(img_array, roi, avg_color)
    
    # Save splits
    for i, split in enumerate(splits):
        # If there's only one split, don't add the number
        if len(splits) == 1:
            output_filename = f"{filename}{extension}"
        else:
            output_filename = f"{filename}_{i+1}{extension}"
        output_path = os.path.join(config["output"], output_filename)
        
        # Convert numpy array back to image and save
        Image.fromarray(split).save(output_path)

def Divide():
    # Create output directory if it doesn't exist
    os.makedirs(config["output"], exist_ok=True)
    
    # Get list of input files
    input_files = [os.path.join(config["input"], f) for f in os.listdir(config["input"])
                    if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Process images in parallel with progress bar
    with ThreadPoolExecutor() as executor:
        list(tqdm(
            executor.map(process_single_image, input_files),
            total=len(input_files),
            desc="Dividing images",
            unit="img"
        ))

if __name__ == "__main__":
    Divide()
