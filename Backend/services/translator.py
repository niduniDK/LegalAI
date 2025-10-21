# pip install transformers sentencepiece

import os
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Support both local and Railway/production paths
if os.path.exists("/app/data"):
    DATA_DIR = "/app/data"  # Railway Volume mount path
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # Local development

MODELS_DIR = os.path.join(DATA_DIR, "models")
m2m100_path = os.path.join(MODELS_DIR, "m2m100_418M")

if not os.path.exists(m2m100_path):
    raise FileNotFoundError(
        f"M2M100 model not found at {m2m100_path}. "
        f"Run 'python download_models.py' to download it."
    )

try:
    tokenizer = M2M100Tokenizer.from_pretrained(m2m100_path)
    model = M2M100ForConditionalGeneration.from_pretrained(m2m100_path)
    print(f"✓ Loaded M2M100 translator from {m2m100_path}")
except Exception as e:
    raise RuntimeError(f"Failed to load M2M100 translator: {e}")

def translate(text, src_language, target_language):
    tokenizer.src_lang = src_language
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id(target_language))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]