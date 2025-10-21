# pip install transformers sentencepiece

import os
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Support both local and Railway/production paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/app/data"):
    DATA_DIR = "/app/data"  # Railway Volume mount path
else:
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # Local development

MODELS_DIR = os.path.join(DATA_DIR, "models")

# Fallback to root data/ if not found in DATA_DIR
if not os.path.exists(os.path.join(MODELS_DIR, "m2m100_418M")):
    fallback = os.path.join(BASE_DIR, "..", "data", "models")
    if os.path.exists(os.path.join(fallback, "m2m100_418M")):
        MODELS_DIR = fallback
        print(f"📁 Using fallback models: {MODELS_DIR}")

m2m100_path = os.path.join(MODELS_DIR, "m2m100_418M")

# Temporarily allow startup without translator for initial deployment
tokenizer = None
model = None

if not os.path.exists(m2m100_path):
    print(f"⚠️ M2M100 model not found at {m2m100_path}. Translation will not be available.")
    print(f"   Run 'python download_models.py' inside the container to download models.")
else:
    try:
        tokenizer = M2M100Tokenizer.from_pretrained(m2m100_path)
        model = M2M100ForConditionalGeneration.from_pretrained(m2m100_path)
        print(f"✓ Loaded M2M100 translator from {m2m100_path}")
    except Exception as e:
        print(f"⚠️ Failed to load M2M100 translator: {e}")

def translate(text, src_language, target_language):
    if model is None or tokenizer is None:
        print(f"⚠️ Translation not available - model not loaded")
        return text  # Return original text if translator not available
    
    tokenizer.src_lang = src_language
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id(target_language))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]