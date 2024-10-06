import os, sys
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
from utils import extract_text_from_pptx


slides = extract_text_from_pptx("data/03-dickinson-basic.pptx")
print(slides)

slides['2']