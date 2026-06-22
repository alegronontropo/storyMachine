import os
import subprocess
import sys

def start_app():
    # פקודה שמריצה את Streamlit ישירות על הקובץ של הלוגיקה
    cmd = ["streamlit", "run", "app.py"]
    subprocess.Popen(cmd)

if __name__ == "__main__":
    start_app()