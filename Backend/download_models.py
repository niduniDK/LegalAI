#!/usr/bin/env python3
"""Download required models to data/models/ for Railway deployment."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def download_legal_bert():
    """Download Legal-BERT model."""
    from sentence_transformers import SentenceTransformer
    
    save_path = MODELS_DIR / "legal-bert-base-uncased"
    if save_path.exists():
        print(f"✓ Legal-BERT already exists at {save_path}")
        return
    
    print("Downloading Legal-BERT (~400MB)...")
    model = SentenceTransformer('nlpaueb/legal-bert-base-uncased')
    model.save(str(save_path))
    print(f"✓ Saved to {save_path}")

def download_translator():
    """Download M2M100 translation model."""
    from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
    
    save_path = MODELS_DIR / "m2m100_418M"
    if save_path.exists():
        print(f"✓ M2M100 already exists at {save_path}")
        return
    
    print("Downloading M2M100 translator (~2GB, may take a few minutes)...")
    tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")
    model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
    tokenizer.save_pretrained(str(save_path))
    model.save_pretrained(str(save_path))
    print(f"✓ Saved to {save_path}")

if __name__ == "__main__":
    print("Downloading models for Railway deployment...\n")
    
    try:
        download_legal_bert()
        print()
        download_translator()
        print("\n✅ All models downloaded successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        exit(1)
