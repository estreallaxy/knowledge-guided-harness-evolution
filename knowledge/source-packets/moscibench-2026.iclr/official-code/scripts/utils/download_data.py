# scripts/utils/download_data.py

import os
import requests
import zipfile
from pathlib import Path
import gdown
from urllib.parse import urlparse

# Available datasets
DATASETS = {
    'terra': 'terra.zip',
    'pop_genetics': 'pop_genetics.zip', 
    'nurse_stress': 'nurse_stress.zip',
    'massspecgym': 'massspecgym.zip',
    'health_spa': 'health_spa.zip',
    'cyclone': 'cyclone.zip'
}

# Google Drive file IDs for each dataset
FILE_IDS = {
    'terra': '1sN7otP9P5BOOrr4mWCY4lKN5akPBZHsF',
    'pop_genetics': '1ZzD14Dec2QgtS2AS85IP8tLWdOaIbN2L',
    'nurse_stress': '14sXqn_f3tQd4zTbmQj-Nz16dIiLYD50N', 
    'massspecgym': '12_HJa5od1IMmyE4es77uD9rixjCrQlRW',
    'health_spa': '1Z9YzslKNx-wHoafTGkiBQaI5FYpLJHsH',
    'cyclone': '1efr6yGGPWxQbo4impExe7ZYiZ6XK6uXT'
}

def download_from_drive(file_id, output_path):
    """Download file from Google Drive using gdown"""
    url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(url, output_path, quiet=False)

def extract_zip(zip_path, extract_to, dataset_name):
    """
    Extract ZIP file to specified directory, ensuring single-level structure
    
    Args:
        zip_path (str): Path to ZIP file
        extract_to (str): Directory to extract to (will be created if not exists)
        dataset_name (str): Name of dataset (used for flattening structure)
    """
    extract_path = Path(extract_to)
    extract_path.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Get all files in the ZIP
        zip_files = zip_ref.namelist()
        
        # Check if there's a top-level directory that matches dataset name
        has_top_level_dir = any(f.startswith(f"{dataset_name}/") for f in zip_files)
        
        if has_top_level_dir:
            # Extract and flatten: remove the top-level directory
            for file_info in zip_ref.infolist():
                if file_info.filename.startswith(f"{dataset_name}/"):
                    # Remove the top-level directory from the path
                    relative_path = file_info.filename[len(f"{dataset_name}/"):]
                    
                    # Skip if it's just the directory entry or empty
                    if not relative_path or relative_path.endswith('/'):
                        continue
                    
                    # Create target path
                    target_path = extract_path / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Extract the file
                    with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                        target.write(source.read())
        else:
            # No top-level directory, extract normally
            zip_ref.extractall(extract_path)
    
    print(f"Extracted {zip_path} to {extract_path}")

def download(dataset_name, data_dir="data", extract=True, remove_zip=True, force_download=False):
    """
    Download and optionally extract a dataset
    
    Args:
        dataset_name (str): Name of the dataset (e.g., 'terra', 'pop_genetics')
        data_dir (str): Directory to save data (default: 'data')
        extract (bool): Whether to extract the ZIP file (default: True)
        remove_zip (bool): Whether to remove ZIP after extraction (default: True)
        force_download (bool): Force re-download even if exists (default: False)
    
    Returns:
        str: Path to downloaded/extracted data
    """
    
    if dataset_name not in DATASETS:
        available = ', '.join(DATASETS.keys())
        raise ValueError(f"Dataset '{dataset_name}' not found. Available: {available}")
    
    # Create data directory
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)
    
    zip_filename = DATASETS[dataset_name]
    zip_path = data_path / zip_filename
    extract_path = data_path / dataset_name
    
    # Check if final dataset already exists (extracted)
    if extract and extract_path.exists() and not force_download:
        print(f"Dataset '{dataset_name}' already exists at {extract_path}")
        return str(extract_path)
    
    # Check if ZIP exists and we don't want to extract
    if not extract and zip_path.exists() and not force_download:
        print(f"Dataset ZIP '{zip_filename}' already exists at {zip_path}")
        return str(zip_path)
    
    # Download if needed
    if not zip_path.exists() or force_download:
        if zip_path.exists():
            print(f"Force re-downloading {zip_filename}...")
        else:
            print(f"Downloading {zip_filename}...")
        
        if dataset_name in FILE_IDS:
            try:
                download_from_drive(FILE_IDS[dataset_name], str(zip_path))
            except Exception as e:
                print(f"Failed to download {zip_filename}: {e}")
                return None
        else:
            print(f"No file ID found for dataset '{dataset_name}'")
            return None
    
    # Extract if requested
    if extract:
        if extract_path.exists() and force_download:
            # Remove existing directory if force download
            import shutil
            shutil.rmtree(extract_path)
            print(f"Removed existing directory {extract_path}")
        
        if not extract_path.exists():
            print(f"Extracting {zip_filename}...")
            extract_zip(str(zip_path), str(extract_path), dataset_name)
        else:
            print(f"Dataset already extracted at {extract_path}")
        
        # Remove ZIP file if requested
        if remove_zip:
            zip_path.unlink()
            print(f"Removed {zip_filename}")
        
        return str(extract_path)
    
    return str(zip_path)

def list_datasets():
    """List all available datasets"""
    print("Available datasets:")
    for name, filename in DATASETS.items():
        print(f"  - {name} ({filename})")

def check_dataset_status(data_dir="data"):
    """Check download status of all datasets"""
    print("Dataset status:")
    data_path = Path(data_dir)
    
    for dataset_name in DATASETS.keys():
        zip_path = data_path / DATASETS[dataset_name]
        extract_path = data_path / dataset_name
        
        status = []
        if zip_path.exists():
            status.append("ZIP downloaded")
        if extract_path.exists():
            status.append("Extracted")
        
        if not status:
            status.append("Not downloaded")
        
        print(f"  - {dataset_name}: {', '.join(status)}")

# Usage example
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Download datasets')
    parser.add_argument('dataset', nargs='?', help='Dataset name to download (optional)')
    parser.add_argument('--data-dir', default='data', help='Data directory')
    parser.add_argument('--no-extract', action='store_true', help='Skip extraction')
    parser.add_argument('--keep-zip', action='store_true', help='Keep ZIP file after extraction')
    parser.add_argument('--force', action='store_true', help='Force re-download even if exists')
    parser.add_argument('--list', action='store_true', help='List available datasets')
    parser.add_argument('--status', action='store_true', help='Check download status of all datasets')
    
    args = parser.parse_args()
    
    if args.list:
        list_datasets()
    elif args.status:
        check_dataset_status(args.data_dir)
    elif args.dataset:
        try:
            path = download(
                args.dataset, 
                data_dir=args.data_dir,
                extract=not args.no_extract,
                remove_zip=not args.keep_zip,
                force_download=args.force
            )
            if path:
                print(f"Dataset available at: {path}")
        except ValueError as e:
            print(f"Error: {e}")
            list_datasets()
    else:
        print("Usage: python download_data.py <dataset_name> [options]")
        print("       python download_data.py --list")
        print("       python download_data.py --status")
        list_datasets()