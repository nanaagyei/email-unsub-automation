"""
Email Unsubscribe Automation - Streamlit Application Entry Point

This is the main entry point for running the Streamlit web interface.

Usage:
    streamlit run app.py
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import and run the Streamlit app
from src.ui.streamlit_app import main

if __name__ == "__main__":
    main()
