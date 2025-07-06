import os
import shutil
from pathlib import Path
import yaml

from Categorize import Categorize
from Divide import Divide
from Maj_Succ import Maj_Succ
from tools import *
from tqdm import tqdm

config = yaml.safe_load(open('config.yaml', 'r'))


if __name__ == "__main__":
    indir = input("Enter the input directory: (or default to 'commission')")
    copy_png_files(source_dir = indir or 'commission' ,target_dir=config['Divide']['input'])
    Divide()
    remove_directory(config['Divide']['input'])
    move_png_files(config['Divide']['output'], config['Keep-Drop']['input'])
    keep_drop()
    copy_png_files("assets/item_template", "Result/item_template")
    