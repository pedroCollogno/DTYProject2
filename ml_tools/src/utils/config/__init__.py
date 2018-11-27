import json
import os

src_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

with open(os.path.join(src_dir, 'config.json'), 'r') as f:
    config = json.load(f)
