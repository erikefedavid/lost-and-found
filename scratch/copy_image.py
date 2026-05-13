import shutil
import os

source = r"C:\Users\Jesus Covenant PC\.gemini\antigravity\brain\339e3078-153b-438c-953e-a1c971c3e9c9\lcu_enhanced_building_1778522345094.png"
dest = r"c:\Users\Jesus Covenant PC\Documents\Jordan's project\lost and found\core\static\core\hero.png"

try:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    shutil.copy(source, dest)
    print("Success")
except Exception as e:
    print(f"Error: {e}")
