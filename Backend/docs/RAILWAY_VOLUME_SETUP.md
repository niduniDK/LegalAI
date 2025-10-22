# Railway Volume Setup & Model Download Guide

## Prerequisites

- Node.js installed on your machine
- Railway account with a deployed project

## Step 1: Install Railway CLI

```powershell
npm install -g @railway/cli
```

## Step 2: Link Your Project

Navigate to your backend directory and link to Railway:

```powershell
cd Backend
railway link
```

Select your project from the list.

## Step 3: Create a Volume

1. Press **Ctrl+K** (or Cmd+K on Mac) in Railway dashboard
2. Type "New Volume" and press Enter
3. Name it: `legalai-volume`
4. Set mount path: `/app/data`
5. Click **Add**

**OR** right-click your service → **Add Volume**

## Step 4: SSH into Railway Container

From your backend directory:

```powershell
railway ssh
```

You should now be inside the Railway container at `/app`.

## Step 5: Download ML Models

### Legal-BERT Model (~440MB)

```bash
mkdir -p /app/data/models/legal-bert-base-uncased
cd /app/data/models/legal-bert-base-uncased

curl -L -o config.json https://huggingface.co/nlpaueb/legal-bert-base-uncased/resolve/main/config.json
curl -L -o pytorch_model.bin https://huggingface.co/nlpaueb/legal-bert-base-uncased/resolve/main/pytorch_model.bin
curl -L -o tokenizer_config.json https://huggingface.co/nlpaueb/legal-bert-base-uncased/resolve/main/tokenizer_config.json
curl -L -o vocab.txt https://huggingface.co/nlpaueb/legal-bert-base-uncased/resolve/main/vocab.txt
curl -L -o special_tokens_map.json https://huggingface.co/nlpaueb/legal-bert-base-uncased/resolve/main/special_tokens_map.json
```

### M2M100 Translation Model (~1.94GB)

```bash
mkdir -p /app/data/models/m2m100_418M
cd /app/data/models/m2m100_418M

curl -L -o config.json https://huggingface.co/facebook/m2m100_418M/resolve/main/config.json
curl -L -o pytorch_model.bin https://huggingface.co/facebook/m2m100_418M/resolve/main/pytorch_model.bin
curl -L -o generation_config.json https://huggingface.co/facebook/m2m100_418M/resolve/main/generation_config.json
curl -L -o sentencepiece.bpe.model https://huggingface.co/facebook/m2m100_418M/resolve/main/sentencepiece.bpe.model
curl -L -o tokenizer_config.json https://huggingface.co/facebook/m2m100_418M/resolve/main/tokenizer_config.json
curl -L -o vocab.json https://huggingface.co/facebook/m2m100_418M/resolve/main/vocab.json
curl -L -o special_tokens_map.json https://huggingface.co/facebook/m2m100_418M/resolve/main/special_tokens_map.json
```

## Step 6: Download Index Files

```bash
mkdir -p /app/data/indices
cd /app/data/indices

curl -L -o acts.faiss https://github.com/Kisara-k/LegalAI-indices/raw/main/acts.faiss
curl -L -o acts.tsv https://github.com/Kisara-k/LegalAI-indices/raw/main/acts.tsv
curl -L -o acts_bm25.pkl https://github.com/Kisara-k/LegalAI-indices/raw/main/acts_bm25.pkl
curl -L -o acts_data.pkl https://github.com/Kisara-k/LegalAI-indices/raw/main/acts_data.pkl
curl -L -o constitution.faiss https://github.com/Kisara-k/LegalAI-indices/raw/main/constitution.faiss
curl -L -o constitution.tsv https://github.com/Kisara-k/LegalAI-indices/raw/main/constitution.tsv
curl -L -o constitution_bm25.pkl https://github.com/Kisara-k/LegalAI-indices/raw/main/constitution_bm25.pkl
```

## Step 7: Verify Files

```bash
# Check models
ls -lh /app/data/models/legal-bert-base-uncased/
ls -lh /app/data/models/m2m100_418M/

# Check indices
ls -lh /app/data/indices/
```

You should see all files with their sizes.

## Step 8: Exit SSH and Restart Service

```bash
exit
```

Then restart your Railway service:

```powershell
railway restart
```

## Troubleshooting

**Q: Downloads are slow?**  
Large files (especially pytorch_model.bin files) take time. The Legal-BERT model is ~440MB and M2M100 is ~1.94GB.

**Q: Connection timeout?**  
Railway containers may sleep. Try the command again or trigger a deployment first.

**Q: Files disappear after restart?**  
Ensure the volume is properly mounted at `/app/data`. Check Railway dashboard → Service → Variables → Mounts.

## Notes

- Total download size: ~2.4GB
- Downloads happen directly in the Railway container
- Files persist in the volume across deployments
- `-L` flag in curl follows redirects (required for Hugging Face and GitHub)
