import zipfile
from pathlib import Path
import sys

if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

root_dir = Path(r'C:\Users\azhar\Desktop\vizualization_Podzim2025')

def unzip_all_automatically(directory: Path):
    for zip_path in directory.rglob('*.zip'):
        extract_to = zip_path.parent / zip_path.stem
        
        extract_to.mkdir(exist_ok=True)
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                print(f"Unzipped: {zip_path.name} -> {extract_to.name}")
        except Exception as e:
            print(f"Error extracting {zip_path.name}: {e}")

if __name__ == "__main__":
    unzip_all_automatically(root_dir)