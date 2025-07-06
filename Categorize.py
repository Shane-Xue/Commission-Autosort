import yaml
import cv2
import os
from tqdm import tqdm

config = yaml.safe_load(open("config.yaml", 'r'))['Categorize']

def load_templates():
    config['match_templ'] = {}
    template_dir = config['Template']
    for template_file in os.listdir(template_dir):
        if template_file.endswith(('.png', '.jpg', '.jpeg')):  # Add more extensions if needed
            name = template_file.split('.')[0]
            template = cv2.imread(os.path.join(template_dir, template_file))
            config['match_templ'][name] = template

def match_image(image_path):
    img = cv2.imread(image_path)
    
    best_match = None
    best_score = config['threshold']
    
    for name, template in config['match_templ'].items():
        # Perform template matching on CPU
        result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val > best_score:
            best_score = max_val
            best_match = name
    
    return best_match

def Categorize():
    load_templates()
    input_dir = config['input']
    output_dir = config['output']

    files = [f for f in os.listdir(input_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    for file in tqdm(files, desc="Processing images", unit="img"):
        file_path = os.path.join(input_dir, file)
        match_result = match_image(file_path)
        
        if match_result:
            match_category = match_result.split('_')[0]
            target_dir = os.path.join(output_dir, match_category)
        else:
            target_dir = os.path.join(output_dir, 'nomatch')

        os.makedirs(target_dir, exist_ok=True)
        os.rename(file_path, os.path.join(target_dir, file))

if __name__ == "__main__":
    Categorize()