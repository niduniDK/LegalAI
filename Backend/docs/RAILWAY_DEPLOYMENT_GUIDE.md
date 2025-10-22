# 🚂 LegalAI Backend Deployment Guide for Railway.com

**Comprehensive step-by-step guide for deploying the LegalAI FastAPI backend to Railway.com**

**Last Updated:** October 21, 2025  
**Target Platform:** Railway.com  
**Frontend Assumption:** Hosted on Vercel

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture Decisions](#architecture-decisions)
4. [Pre-Deployment Setup](#pre-deployment-setup)
5. [Railway Project Setup](#railway-project-setup)
6. [Storage Configuration](#storage-configuration)
7. [Environment Variables](#environment-variables)
8. [Deployment Process](#deployment-process)
9. [Post-Deployment](#post-deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This guide walks you through deploying the LegalAI backend to Railway.com, including:

- Setting up persistent storage for vector databases and ML models
- Configuring environment variables
- Handling ML model downloads (Legal-BERT)
- Connecting to your database and frontend

**Deployment Stack:**

- **Backend Hosting:** Railway.com
- **Frontend Hosting:** Vercel (assumed)
- **Database:** Supabase/Neon PostgreSQL (from your .env)
- **Storage:** Railway Volumes (for docs and models)

---

## ✅ Prerequisites

Before starting, ensure you have:

- [ ] Railway.com account (Sign up at https://railway.app/)
- [ ] GitHub account with your LegalAI repository
- [ ] Database credentials (Supabase/Neon PostgreSQL)
- [ ] API keys ready:
  - GEMINI_API_KEY or OPENAI_API_KEY
  - JWT_SECRET_KEY
  - SMTP credentials (for email)
  - LANGSMITH_API_KEY (optional)
- [ ] Vercel frontend URL (for CORS configuration)
- [ ] Git repository pushed to GitHub

---

## 🏗️ Architecture Decisions

### Decision 1: Storage for Indices and Models

**Solution:** Use **Railway Volumes** with structured data folder

**Folder Structure:**

```
data/
├── indices/          # FAISS indices, BM25 pickles, TSV files (~47MB)
│   ├── acts.faiss
│   ├── acts_bm25.pkl
│   ├── acts.tsv
│   ├── constitution.faiss
│   ├── constitution_bm25.pkl
│   ├── constitution.tsv
│   └── ...
└── models/           # Legal-BERT model (~400MB)
    └── legal-bert-base-uncased/
        ├── config.json
        ├── pytorch_model.bin
        ├── tokenizer_config.json
        └── ...
```

**Rationale:**

- Separates indices and models for better organization
- All data is static after preprocessing
- Railway Volumes provide persistent storage that survives deployments
- Volume mounting is fast and reliable for read-heavy operations
- Legal-BERT loaded from volume = no runtime downloads = faster cold starts

**Implementation:**

- Mount a Railway Volume to `/app/data`
- Copy data structure to volume on first deployment
- Application loads both indices and model from volume

---

## 🔧 Pre-Deployment Setup

### Step 1: Prepare Your Repository

1. **Create a `Procfile`** in `Backend/` directory (tells Railway how to start your app):

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. **Create a `runtime.txt`** in `Backend/` directory (specifies Python version):

```
python-3.11.9
```

3. **Create a `railway.toml`** in `Backend/` directory (Railway configuration):

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
```

4. **Update `main.py` CORS Configuration** (if not already done):

Replace the CORS middleware section with:

```python
# Get frontend URL from environment variable
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Configure CORS
allowed_origins = [
    FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add additional origins if provided
additional_origins = os.getenv("ADDITIONAL_CORS_ORIGINS", "")
if additional_origins:
    allowed_origins.extend(additional_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

5. **Update `services/langchain_retriever.py` for flexible path handling**:

The code is already updated to support both local and Railway paths:

```python
# Support both local and Railway/production paths
if os.path.exists("/app/data"):
    DATA_DIR = "/app/data"  # Railway Volume mount path
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "..", "data")  # Local development

# Subfolders for different data types
INDICES_DIR = os.path.join(DATA_DIR, "indices")  # For .faiss, .pkl, .tsv files
MODELS_DIR = os.path.join(DATA_DIR, "models")     # For Legal-BERT model
```

6. **Commit and push changes**:

```bash
git add Backend/Procfile Backend/runtime.txt Backend/railway.toml Backend/main.py Backend/services/langchain_retriever.py Backend/copy_docs_to_volume.py
git commit -m "Add Railway deployment configuration with structured data folder"
git push origin main
```

---

## 🚂 Railway Project Setup

### Step 2: Create Railway Project

1. **Log in to Railway:**

   - Go to https://railway.app/
   - Sign in with GitHub

2. **Create a New Project:**

   - Click **"New Project"**
   - Select **"Deploy from GitHub repo"**
   - Authorize Railway to access your repositories
   - Select your **LegalAI** repository
   - Railway will detect your app automatically

3. **Configure Build Settings:**

   - Railway will **auto-detect Python** from `requirements.txt`
   - It uses **Nixpacks** buildpack by default (no Docker needed!)
   - If needed, go to **Settings** > **Build**
   - Confirm **Builder**: Nixpacks (Python)
   - Set **Root Directory**: `Backend` (if your repo has multiple folders)
   - Railway will automatically:
     - Detect Python from `requirements.txt`
     - Install dependencies with pip
     - Use the `Procfile` to start your app

4. **Generate Domain:**
   - Go to **Settings** > **Networking**
   - Click **"Generate Domain"**
   - Copy the generated URL (e.g., `your-app.up.railway.app`)
   - Save this URL - you'll need it for frontend configuration

---

## 💾 Storage Configuration

### Step 3: Create and Mount Railway Volume

Railway Volumes provide persistent storage for your vector databases and indices.

1. **Create a Volume:**

   - In your Railway project dashboard
   - Click on your service
   - Go to the **"Data"** or **"Volumes"** tab
   - Click **"New Volume"**
   - Name it: `legalai-data-storage`
   - Set size: **1 GB** (indices ~47MB + Legal-BERT ~400MB = plenty of room)

2. **Mount the Volume:**

   - In the Volume settings
   - Set **Mount Path**: `/app/data`
   - Click **"Save"**

3. **Upload Your Data to the Volume:**

   **Option A: Using Railway CLI (Recommended)**

   ```bash
   # Install Railway CLI
   npm install -g @railway/cli

   # Login to Railway
   railway login

   # Link to your project
   railway link

   # Shell into your running service
   railway shell

   # Then from another terminal, copy files (Railway doesn't support direct file upload yet)
   # You'll need to use one of the other methods below
   ```

   **Option B: Bundle data with your repository (Recommended - Simplest)**

   Since your data folder is ~450-500MB total, you can:

   - Keep `Backend/data/` in your git repository with structure:
     ```
     Backend/data/
     ├── indices/    # .faiss, .pkl, .tsv files
     └── models/     # Legal-BERT model
     ```
   - Railway deploys it with your code
   - The startup script `copy_docs_to_volume.py` (already created) copies to volume

   The `Procfile` already includes:

   ```
   web: python copy_docs_to_volume.py && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

   This automatically:

   - Checks if volume is mounted at `/app/data`
   - Copies `data/indices/` contents to `/app/data/indices/`
   - Copies `data/models/` contents to `/app/data/models/`
   - Skips copying if volume already has data

   **Option C: Download from External Storage (Production-ready for very large files)**

   Upload your data to cloud storage (AWS S3, Google Cloud Storage, etc.) and download on startup:

   ```python
   # download_data.py
   import os
   import requests

   DATA_URL = "https://your-storage-url.com/data.tar.gz"
   DATA_DIR = "/app/data"

   if not os.path.exists(f"{DATA_DIR}/indices/acts.faiss"):
       print("📥 Downloading data...")
       # Download and extract logic here
   ```

   **Option D: Use Railway's Web Shell**

   ```bash
   # In Railway dashboard
   # Go to your service > "..." menu > "Shell"
   # Upload files using wget or curl:
   cd /app/data/indices
   wget https://your-storage-url.com/acts.faiss
   wget https://your-storage-url.com/acts_bm25.pkl
   # ... etc

   cd /app/data/models
   # Upload Legal-BERT model files
   ```

4. **Verify Mount:**
   - After deployment, open Railway Shell
   - Run: `ls -la /app/data`
   - You should see: `indices/` and `models/` subdirectories
   - Check contents: `ls -la /app/data/indices` and `ls -la /app/data/models`

---

## 🔐 Environment Variables

### Step 4: Configure Environment Variables in Railway

1. **Go to your service in Railway Dashboard**
2. **Navigate to "Variables" tab**
3. **Add the following environment variables:**

```bash
# Database Configuration
DATABASE_URL=postgresql://your-user:your-password@your-host.pooler.supabase.com:6543/postgres
POSTGRES_HOST=your-host.pooler.supabase.com
POSTGRES_USER=your-user
POSTGRES_PASSWORD=your-password
POSTGRES_PORT=6543
POSTGRES_DB=postgres
POSTGRES_SSL=require

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=LegalAI Support

# API Keys
GEMINI_API_KEY=your-gemini-api-key
OPENAI_API_KEY=your-openai-api-key

# LLM Configuration
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp

# Application Settings
APP_NAME=LegalAI
APP_URL=https://your-frontend.vercel.app
API_URL=https://your-app.up.railway.app
ENVIRONMENT=production
FRONTEND_URL=https://your-frontend.vercel.app

# CORS Additional Origins (comma-separated, optional)
ADDITIONAL_CORS_ORIGINS=https://your-custom-domain.com

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_REQUESTS_PER_HOUR=1000

# Session Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax

# LangSmith (Optional - for observability)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_PROJECT=legalai-production
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_TRACING_V2=true

# Railway Specific (Auto-set by Railway)
# PORT - Automatically set by Railway (usually 8000 or dynamic)
```

**Important Notes:**

- **Don't add `PORT`** - Railway sets this automatically
- **Use production-grade secrets** - Generate strong random strings for JWT_SECRET_KEY
- **FRONTEND_URL** - Must be your actual Vercel deployment URL
- **DATABASE_URL** - Use your Supabase connection pooler URL for better performance
- **SMTP_PASSWORD** - For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password

4. **Click "Save" or "Deploy"** after adding variables

---

## 🚀 Deployment Process

### Step 5: Deploy to Railway

1. **Trigger Deployment:**

   - Railway automatically deploys on git push to main branch
   - Or click **"Deploy"** button in Railway dashboard
   - Or manually trigger: `railway up` (using Railway CLI)

2. **Monitor Build Logs:**

   - Click on your service
   - Go to **"Deployments"** tab
   - Click on the active deployment
   - Watch the build logs for errors

3. **Build Process Timeline:**

   ```
   [1/4] Cloning repository...
   [2/4] Detecting Python environment (Nixpacks)...
   [3/4] Installing dependencies from requirements.txt (~3-5 minutes)...
   [4/4] Starting application with Procfile command...
   ```

4. **Expected Startup Behavior:**

   - Application starts on port 8000 (or Railway's $PORT)
   - Database connection test runs
   - Legal-BERT model downloads on first query (~1-2 minutes)
   - FAISS indices load from mounted volume
   - Health check passes at `/` endpoint

5. **Check Deployment Status:**
   - Look for **"Active"** status in Railway dashboard
   - Green checkmark indicates successful deployment

---

## ✅ Post-Deployment

### Step 6: Verify Deployment

1. **Test Health Endpoint:**

   ```bash
   curl https://your-app.up.railway.app/
   # Should return: {"message": "Welcome to LegalAI API"}
   ```

2. **Test API Documentation:**

   - Visit: `https://your-app.up.railway.app/docs`
   - Should see FastAPI Swagger UI

3. **Test Database Connection:**

   - Check Railway logs for: `✅ Database connected successfully!`
   - If failed, verify DATABASE_URL in environment variables

4. **Test Document Retrieval:**

   - Make a test query to `/get_ai_response` endpoint
   - Check logs for: `✅ Retriever pre-loaded successfully!`
   - First query may be slow (model download)

5. **Monitor Logs:**

   ```bash
   # Using Railway CLIhow does this
   railway logs

   # Or in Railway Dashboard
   # Service > Logs tab
   ```

### Step 7: Configure Frontend (Vercel)

Update your frontend environment variables on Vercel:

1. **Go to Vercel Dashboard**
2. **Select your project** > **Settings** > **Environment Variables**
3. **Add/Update:**

   ```bash
   NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
   NEXT_PUBLIC_API_BASE_URL=https://your-app.up.railway.app
   ```

4. **Redeploy frontend** to apply changes

### Step 8: Test End-to-End

1. **Open your Vercel frontend**
2. **Test user registration/login**
3. **Test chat functionality**
4. **Test search features**
5. **Monitor both Railway and Vercel logs**

---

## 🔧 Troubleshooting

### Issue 1: Data Not Found / FAISS Load Error

**Symptoms:**

```
FileNotFoundError: [Errno 2] No such file or directory: '/app/data/indices/acts.faiss'
```

**Solutions:**

1. Verify Volume is mounted to `/app/data`
2. Check Volume contents in Railway Shell: `ls -la /app/data`
3. Check subdirectories: `ls -la /app/data/indices` and `ls -la /app/data/models`
4. Re-upload data if empty
5. Verify path in `langchain_retriever.py` matches mount point

### Issue 2: Database Connection Failed

**Symptoms:**

```
⚠️  WARNING: Database connection failed!
```

**Solutions:**

1. Check DATABASE_URL format: `postgresql+pg8000://user:pass@host:port/db`
2. Verify database is accessible from Railway (check firewall/allowlist)
3. For Supabase: Use connection pooler URL (port 6543)
4. Test connection manually: `railway run python test_db.py`

### Issue 3: Legal-BERT Model Not Loading

**Symptoms:**

```
⚠ Legal-BERT not found in: /app/data/models/legal-bert-base-uncased
Using fallback model: all-MiniLM-L6-v2
```

**Solutions:**

1. Verify Legal-BERT model is in `/app/data/models/legal-bert-base-uncased/`
2. Check model files exist:
   ```bash
   ls -la /app/data/models/legal-bert-base-uncased/
   # Should see: config.json, pytorch_model.bin, tokenizer files, etc.
   ```
3. If not in volume, it will try to download from HuggingFace (takes 1-2 min first time)
4. Fallback model `all-MiniLM-L6-v2` will be used if download fails
5. To pre-download Legal-BERT locally:
   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('nlpaueb/legal-bert-base-uncased')
   model.save('Backend/data/models/legal-bert-base-uncased')
   ```

### Issue 4: CORS Errors from Frontend

**Symptoms:**

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions:**

1. Verify `FRONTEND_URL` environment variable is set correctly
2. Check CORS configuration in `main.py`
3. Ensure frontend is using correct API URL
4. Add additional origins to `ADDITIONAL_CORS_ORIGINS` if needed

### Issue 5: Memory Issues / OOM (Out of Memory)

**Symptoms:**

```
Container killed due to memory limit
```

**Solutions:**

1. Railway free tier: 512MB RAM, Pro: 8GB
2. Upgrade Railway plan if needed
3. Optimize model loading - ensure caching works
4. Check for memory leaks in logs
5. Consider using smaller embedding model as fallback

### Issue 6: Slow First Request

**Symptoms:**

- First API call takes 2-3 minutes

**Solutions:**

- This is **EXPECTED** behavior
- Legal-BERT model downloads on first use (~400MB)
- Subsequent requests will be fast
- To avoid: Pre-download model in Dockerfile (increases build time)

### Issue 7: Environment Variables Not Loading

**Symptoms:**

```
ValueError: GEMINI_API_KEY not found in environment variables
```

**Solutions:**

1. Verify variables are set in Railway dashboard
2. Redeploy after adding variables
3. Check for typos in variable names
4. Use Railway CLI: `railway variables`

---

## 📊 Railway Configuration Summary

| Setting              | Value                                                          |
| -------------------- | -------------------------------------------------------------- |
| **Builder**          | Nixpacks (Python auto-detection)                               |
| **Root Directory**   | `Backend`                                                      |
| **Start Command**    | `uvicorn main:app --host 0.0.0.0 --port $PORT` (from Procfile) |
| **Python Version**   | 3.11.9 (from runtime.txt)                                      |
| **Volume Mount**     | `/app/data`                                                    |
| **Volume Size**      | 1 GB                                                           |
| **Volume Structure** | `indices/` and `models/` subdirectories                        |
| **Health Check**     | `/` endpoint                                                   |
| **Port**             | Auto-assigned by Railway ($PORT)                               |

---

## 📝 Maintenance & Updates

### Updating Data (Vector Indices or Model)

1. **Update locally** and regenerate indices or update model
2. **Upload to Railway Volume:**
   ```bash
   railway shell
   # Upload new files via SCP or git
   ```
3. **Restart service** to load new data

### Updating Code

1. **Commit and push to GitHub**
2. **Railway auto-deploys** on push
3. **Monitor logs** for successful deployment

### Monitoring

- **Railway Dashboard** - Real-time logs and metrics
- **LangSmith** - LLM call tracing (if enabled)
- **Supabase Dashboard** - Database metrics

---

## 🎯 Deployment Checklist

Before going live, ensure:

- [ ] All environment variables are set in Railway
- [ ] Volume is mounted and data (indices + models) are uploaded
- [ ] Database connection is successful
- [ ] Frontend URL is configured for CORS
- [ ] API domain is generated and accessible
- [ ] Frontend is updated with Railway API URL
- [ ] Test all major API endpoints
- [ ] Monitor logs for errors
- [ ] Set up error alerting (Railway notifications)
- [ ] Document your Railway URL and credentials

---

## 🔗 Useful Links

- **Railway Dashboard:** https://railway.app/dashboard
- **Railway CLI Docs:** https://docs.railway.app/develop/cli
- **Railway Volumes:** https://docs.railway.app/reference/volumes
- **Supabase Dashboard:** https://supabase.com/dashboard
- **LangSmith:** https://smith.langchain.com/

---

## 💡 Cost Optimization Tips

1. **Use Railway Hobby Plan** ($5/month) for testing
2. **Railway auto-scales** based on usage - no manual configuration needed
3. **Use connection pooling** for database (already configured)
4. **Monitor usage** in Railway dashboard
5. **Consider model caching** to reduce cold start times
6. **Nixpacks is optimized** - faster builds than Docker
7. **Scale up only when needed** - Railway allows easy scaling

---

## 🎉 Success!

Your LegalAI backend is now live on Railway! 🚀

**Next Steps:**

1. Share your API URL with your team
2. Monitor performance and logs
3. Set up automated backups for your database
4. Consider adding CI/CD pipelines for testing
5. Scale as your user base grows

---

**Questions or Issues?**

- Check Railway documentation
- Review application logs
- Test locally first with Docker
- Verify all environment variables

**Happy Deploying! 🚂**
