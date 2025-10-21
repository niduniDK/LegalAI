"""
Script to copy data (indices and models) from repository to Railway Volume on first deployment.
This ensures the volume has all necessary FAISS indices, BM25 pickles, TSV files, and Legal-BERT model.
"""

import os
import shutil

# Source directories (in the repository)
SOURCE_DATA_DIR = "./data"
SOURCE_INDICES_DIR = "./data/indices"
SOURCE_MODELS_DIR = "./data/models"

# Target volume mount point (Railway Volume)
VOLUME_DATA_DIR = "/app/data"
VOLUME_INDICES_DIR = "/app/data/indices"
VOLUME_MODELS_DIR = "/app/data/models"

def copy_data_to_volume():
    """Copy data (indices and models) to volume if volume is mounted and empty."""
    
    # Check if volume is mounted
    if not os.path.exists(VOLUME_DATA_DIR):
        print("ℹ️  Volume not mounted at /app/data, using local data folder")
        return
    
    if not os.path.isdir(VOLUME_DATA_DIR):
        print("⚠️  /app/data exists but is not a directory")
        return
    
    print("📦 Checking Railway Volume for data...")
    
    # Create subdirectories in volume if they don't exist
    os.makedirs(VOLUME_INDICES_DIR, exist_ok=True)
    os.makedirs(VOLUME_MODELS_DIR, exist_ok=True)
    
    # Copy indices (.faiss, .pkl, .tsv files)
    if os.path.exists(SOURCE_INDICES_DIR):
        indices_files = os.listdir(SOURCE_INDICES_DIR)
        volume_indices_files = os.listdir(VOLUME_INDICES_DIR)
        
        if not volume_indices_files:
            print(f"📁 Copying indices to volume ({len(indices_files)} files)...")
            for item in indices_files:
                source_path = os.path.join(SOURCE_INDICES_DIR, item)
                dest_path = os.path.join(VOLUME_INDICES_DIR, item)
                
                try:
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, dest_path)
                        print(f"   ✓ Copied: {item}")
                    elif os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                        print(f"   ✓ Copied directory: {item}")
                except Exception as e:
                    print(f"   ⚠️  Failed to copy {item}: {e}")
            
            print("✅ Indices copied to volume!")
        else:
            print(f"✅ Volume already has {len(volume_indices_files)} indices files")
    else:
        print(f"⚠️  Source indices directory not found: {SOURCE_INDICES_DIR}")
    
    # Copy models (Legal-BERT)
    if os.path.exists(SOURCE_MODELS_DIR):
        models = os.listdir(SOURCE_MODELS_DIR)
        volume_models = os.listdir(VOLUME_MODELS_DIR)
        
        if not volume_models:
            print(f"🤖 Copying models to volume ({len(models)} models)...")
            for item in models:
                source_path = os.path.join(SOURCE_MODELS_DIR, item)
                dest_path = os.path.join(VOLUME_MODELS_DIR, item)
                
                try:
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, dest_path)
                        print(f"   ✓ Copied: {item}")
                    elif os.path.isdir(source_path):
                        shutil.copytree(source_path, dest_path)
                        print(f"   ✓ Copied model: {item}")
                except Exception as e:
                    print(f"   ⚠️  Failed to copy {item}: {e}")
            
            print("✅ Models copied to volume!")
        else:
            print(f"✅ Volume already has {len(volume_models)} models")
    else:
        print(f"⚠️  Source models directory not found: {SOURCE_MODELS_DIR}")
    
    print("="*60)

if __name__ == "__main__":
    copy_data_to_volume()
