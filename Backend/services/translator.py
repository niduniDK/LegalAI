# pip install transformers sentencepiece

from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# Load model
model_name = "facebook/m2m100_418M"
tokenizer = M2M100Tokenizer.from_pretrained(model_name)
model = M2M100ForConditionalGeneration.from_pretrained(model_name)

def translate(text, src_language, target_language):
    tokenizer.src_lang = src_language
    encoded = tokenizer(text, return_tensors="pt")
    generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.get_lang_id(target_language))
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]