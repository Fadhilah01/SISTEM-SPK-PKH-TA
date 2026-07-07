import sys
import os

# Add the 'web' directory to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

from app import create_app

app = create_app()
