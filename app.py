"""
AI Resume Analyzer - Main Application File
This is the entry point for running the Streamlit application
"""

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Streamlit UI
if __name__ == "__main__":
    print("Starting AI Resume Analyzer...")
    print("Navigate to the URL shown below in your browser")
    print("-" * 50)
    
    # Run the Streamlit app
    import streamlit.web.cli as stcli
    
    ui_file = os.path.join(os.path.dirname(__file__), 'ui', 'streamlit_ui.py')
    sys.argv = ["streamlit", "run", ui_file]
    sys.exit(stcli.main())

# ------
# import os
# import subprocess
# import sys

# if __name__ == "__main__":
#     print("Starting AI Resume Analyzer...")
#     print("Navigate to the URL shown below in your browser")
#     print("-" * 50)

#     ui_file = os.path.join(os.path.dirname(__file__), "ui", "streamlit_ui.py")

#     subprocess.run([
#         sys.executable,
#         "-m",
#         "streamlit",
#         "run",
#         ui_file
#     ])
