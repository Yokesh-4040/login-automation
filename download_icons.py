import requests
from pathlib import Path

def download_icon(url, filename):
    icons_dir = Path("Icons")
    if not icons_dir.exists():
        icons_dir.mkdir()
        
    filepath = icons_dir / filename
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

# Icon URLs (using Material Design Icons)
icons = {
    "profile.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/social/person/materialicons/24dp/2x/baseline_person_black_24dp.png",
    "eye.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/visibility/materialicons/24dp/2x/baseline_visibility_black_24dp.png",
    "eye_off.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/action/visibility_off/materialicons/24dp/2x/baseline_visibility_off_black_24dp.png",
    "close.png": "https://raw.githubusercontent.com/google/material-design-icons/master/png/navigation/close/materialicons/24dp/2x/baseline_close_black_24dp.png"
}

if __name__ == "__main__":
    print("Downloading icons...")
    for filename, url in icons.items():
        download_icon(url, filename)
    print("Done!") 