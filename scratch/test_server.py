import urllib.request
import sys
import subprocess
import time
import os

def main():
    print("Starting Django server for verification...")
    # Start the django server on a different port to avoid conflict
    proc = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8088"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Fetch the home page
        print("Fetching landing page...")
        url = "http://127.0.0.1:8088/"
        response = urllib.request.urlopen(url)
        html = response.read().decode('utf-8')
        
        # Search for the image tag
        print("\nSearching for hero image tag in HTML:")
        for line in html.split('\n'):
            if 'hero.png' in line or 'hero_image' in line or 'hero' in line:
                if 'img' in line or 'src' in line:
                    print(line.strip())
                    
        # Check if the static image returns a 200
        print("\nVerifying static image resource accessibility:")
        static_url = "http://127.0.0.1:8088/static/core/hero.png"
        try:
            img_resp = urllib.request.urlopen(static_url)
            print(f"Success! /static/core/hero.png returned HTTP {img_resp.status} (Length: {img_resp.headers.get('Content-Length')})")
        except Exception as e:
            print(f"FAILED to fetch image: {e}")
            
    except Exception as e:
        print(f"Error fetching: {e}")
    finally:
        print("Terminating test server...")
        proc.terminate()

if __name__ == "__main__":
    main()
