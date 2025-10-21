# 🚂 Railway Deployment - Quick Reference

## Essential Files Created

```
Backend/
├── Procfile                     # Tells Railway how to start the app
├── runtime.txt                  # Specifies Python version (3.11.9)
├── railway.toml                 # Railway configuration
├── copy_docs_to_volume.py       # Copies docs to Railway Volume on startup
└── RAILWAY_DEPLOYMENT_GUIDE.md  # Full detailed guide
```

## Quick Deploy Steps

1. **Push to GitHub**

   ```bash
   git add Backend/Procfile Backend/runtime.txt Backend/railway.toml Backend/copy_docs_to_volume.py
   git commit -m "Add Railway deployment files"
   git push origin main
   ```

2. **Create Railway Project**

   - Go to https://railway.app/
   - "New Project" → "Deploy from GitHub repo"
   - Select your LegalAI repository
   - Set Root Directory: `Backend`

3. **Create Volume**

   - In Railway dashboard: Press `Ctrl+K` (or `⌘K` on Mac) to open Command Palette
   - Or right-click on the project canvas
   - Select "New Volume"
   - Connect it to your service
   - Set mount path: `/app/docs`
   - Default size starts at 0.5GB (Free/Trial) or 5GB (Hobby) - can grow later

4. **Set Environment Variables**

   - Copy from `.env.example`
   - Add `FRONTEND_URL=https://your-vercel-app.vercel.app`
   - **Critical vars:** DATABASE_URL, GEMINI_API_KEY, JWT_SECRET_KEY, SMTP credentials

5. **Deploy!**
   - Railway auto-deploys
   - Get your URL from "Settings" → "Networking" → "Generate Domain"

## Environment Variables Checklist

```bash
# Required
DATABASE_URL=postgresql://...
GEMINI_API_KEY=...
JWT_SECRET_KEY=...
FRONTEND_URL=https://your-app.vercel.app

# Email (Required for auth)
SMTP_USERNAME=...
SMTP_PASSWORD=...
SMTP_FROM_EMAIL=...

# Optional but recommended
LANGSMITH_API_KEY=...
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
```

## Update Frontend (Vercel)

In Vercel environment variables:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app
```

## How It Works

1. **No Docker needed!** Railway uses Nixpacks to auto-detect Python
2. **Docs are copied** from your repo to the Railway Volume on first startup
3. **Legal-BERT model** downloads automatically on first query (~1-2 min)
4. **Subsequent requests** are fast (model and docs are cached)

## Troubleshooting Quick Fixes

| Issue               | Solution                            |
| ------------------- | ----------------------------------- |
| Docs not found      | Check Volume mounted at `/app/docs` |
| Database error      | Verify DATABASE_URL format          |
| CORS error          | Check FRONTEND_URL env var          |
| Model download slow | Normal on first request (2 min)     |
| Build fails         | Check requirements.txt has all deps |

## Useful Commands

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and link project
railway login
railway link

# View logs
railway logs

# Open shell
railway shell

# Set environment variable
railway variables set KEY=VALUE
```

## Cost Estimate

- **Hobby Plan:** $5/month (500 hours)
- **Volume Storage:** 1GB = ~$0.25/month
- **Typical usage:** ~$5-10/month for small projects

## What Railway Does Automatically

✅ Detects Python from `requirements.txt`  
✅ Installs dependencies with pip  
✅ Uses `Procfile` to start your app  
✅ Assigns a port ($PORT)  
✅ Generates HTTPS domain  
✅ Auto-redeploys on git push  
✅ Provides logs and metrics  
✅ SSL certificates

## Need More Help?

📖 Read the full guide: `RAILWAY_DEPLOYMENT_GUIDE.md`  
🔗 Railway Docs: https://docs.railway.app/  
💬 Railway Discord: https://discord.gg/railway

---

**Pro Tip:** Test locally first with:

```bash
cd Backend
uvicorn main:app --reload --port 8000
```

Then visit http://localhost:8000/docs to ensure everything works!
