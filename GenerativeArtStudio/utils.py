# utils.py

import os
from datetime import datetime

def ensure_output_dir():
    output_dir = "outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def get_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
