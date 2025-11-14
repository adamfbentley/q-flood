# Q-Flood Deployment Guide

This guide covers deploying Q-Flood to free cloud platforms.

## 🌐 Architecture

- **Frontend**: Vercel (React/Vite static site)
- **Backend**: Railway or Render (FastAPI with SQLite)

---

## 📦 Prerequisites

1. GitHub account (for deployments)
2. Accounts on:
   - [Vercel](https://vercel.com) (frontend)
   - [Railway](https://railway.app) OR [Render](https://render.com) (backend)

---

## 🚀 Backend Deployment (Railway - Recommended)

### Option A: Railway (Easier, Better Free Tier)

1. **Sign up at [Railway.app](https://railway.app)** with GitHub

2. **Create New Project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose `q-flood` repository
   - Select the `main` branch

3. **Configure Environment Variables**:
   ```
   DATABASE_URL=sqlite:///./qflood.db
   POSTGRES_DB=qflood
   POSTGRES_USER=dev
   POSTGRES_PASSWORD=dev
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET_NAME=qflood-data
   MINIO_SECURE=false
   API_KEY_HASH_SALT=production-salt-change-this-value
   REDIS_URL=redis://localhost:6379/0
   APP_ENV=production
   PORT=8000
   ```

4. **Deploy**:
   - Railway will auto-detect Python and deploy
   - Wait for build to complete (~3-5 minutes)
   - Copy the generated URL (e.g., `https://qflood-production.up.railway.app`)

5. **Notes**:
   - Free tier: 500 hours/month, $5 credit
   - SQLite-only (no PostgreSQL on free tier)
   - No MinIO or Redis (features will be disabled)

---

### Option B: Render

1. **Sign up at [Render.com](https://render.com)** with GitHub

2. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your `q-flood` repository
   - Select the `main` branch

3. **Configure**:
   - **Name**: `qflood-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** (same as Railway above)

5. **Deploy**:
   - Click "Create Web Service"
   - Wait for deployment (~5-10 minutes)
   - Copy the service URL

6. **Notes**:
   - Free tier: 750 hours/month but spins down after 15min inactivity
   - First request after sleep takes ~30-60 seconds to wake up

---

## 🎨 Frontend Deployment (Vercel)

1. **Sign up at [Vercel.com](https://vercel.com)** with GitHub

2. **Import Project**:
   - Click "Add New" → "Project"
   - Import `q-flood` repository
   - Framework: Vite
   - Root Directory: `frontend`

3. **Configure Build Settings**:
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. **Set Environment Variable**:
   ```
   VITE_API_URL=https://your-railway-or-render-url.app
   ```
   (Use the backend URL from Step 1)

5. **Deploy**:
   - Click "Deploy"
   - Wait for build (~2-3 minutes)
   - Visit your live URL (e.g., `https://qflood.vercel.app`)

---

## ✅ Verify Deployment

### Test Backend:
```bash
curl https://your-backend-url.app/
# Should return: {"message":"Welcome to the Quantum Flood Forecasting Framework API"}
```

### Test API Docs:
Visit: `https://your-backend-url.app/docs`

### Test Frontend:
Visit your Vercel URL and ensure:
- Page loads without errors
- Can navigate between pages
- API calls work (check browser console)

---

## 🔧 Troubleshooting

### Backend Issues:

**"Module not found" errors**:
- Check `requirements.txt` includes all dependencies
- Railway/Render may need: `pip install --upgrade pip`

**Database errors**:
- Ensure `DATABASE_URL=sqlite:///./qflood.db` is set
- SQLite only on free tiers (no PostgreSQL)

**App not starting**:
- Check logs in Railway/Render dashboard
- Verify `PORT` environment variable is set
- Ensure start command uses `--host 0.0.0.0`

### Frontend Issues:

**API calls failing**:
- Check `VITE_API_URL` environment variable
- Must include `https://` protocol
- Check CORS settings in backend (should allow your Vercel domain)

**Build errors**:
- Check Node.js version (should be 18+)
- Try: `npm install` locally first
- Check for TypeScript errors

**Blank page**:
- Check browser console for errors
- Verify `dist` folder is being served
- Check Vercel build logs

---

## 🔄 Continuous Deployment

Both platforms support auto-deploy on git push:

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Update deployment"
   git push origin main
   ```

2. **Automatic Deployment**:
   - Vercel rebuilds frontend automatically
   - Railway/Render rebuilds backend automatically
   - Usually takes 2-5 minutes

---

## 💰 Cost Considerations

### Free Tier Limits:

**Vercel**:
- ✅ 100GB bandwidth/month
- ✅ Unlimited sites
- ✅ Automatic HTTPS
- ⚠️ Commercial use requires Pro ($20/mo)

**Railway**:
- ✅ $5 credit/month (≈500 hours)
- ✅ Always-on with credit
- ⚠️ Overages billed at $0.000231/min

**Render**:
- ✅ 750 hours/month free
- ⚠️ Spins down after 15min idle
- ⚠️ Slow cold starts (30-60s)

### Recommended for Q-Flood:
- **Development**: Railway (always-on, good DX)
- **Portfolio/Demo**: Vercel + Render (fully free)
- **Production**: Railway Hobby ($5/mo) or fly.io

---

## 🌐 Custom Domain (Optional)

### Vercel (Frontend):
1. Go to Project Settings → Domains
2. Add your domain (e.g., `qflood.yourdomain.com`)
3. Update DNS records as shown
4. Auto HTTPS certificate

### Railway (Backend):
1. Go to Settings → Public Networking
2. Generate domain or add custom
3. Update frontend `VITE_API_URL`

---

## 📊 Monitoring

### Railway:
- Dashboard → Metrics tab
- CPU, Memory, Network usage
- Build and deploy logs

### Render:
- Dashboard → Logs tab
- Real-time application logs
- Health check status

### Vercel:
- Analytics dashboard
- Edge network performance
- Error tracking (Vercel Pro)

---

## 🔒 Security Checklist

Before deploying:

- [ ] Change `API_KEY_HASH_SALT` to random string
- [ ] Set `APP_ENV=production`
- [ ] Remove any test/debug endpoints
- [ ] Enable CORS for specific domains only
- [ ] Add rate limiting (if possible)
- [ ] Review `.gitignore` (no secrets committed)

---

## 📝 Post-Deployment

1. **Update GitHub README** with live URLs:
   ```markdown
   ## 🌐 Live Demo
   - Frontend: https://qflood.vercel.app
   - API Docs: https://qflood-api.up.railway.app/docs
   ```

2. **Add to LinkedIn/CV**:
   - "Live Demo" link
   - Screenshots of working app
   - Technical architecture diagram

3. **Monitor First Week**:
   - Check error logs daily
   - Monitor resource usage
   - Test all features work

---

## 🆘 Support

- **Railway**: [Discord](https://discord.gg/railway)
- **Render**: [Community Forum](https://community.render.com)
- **Vercel**: [Documentation](https://vercel.com/docs)

---

## 🎯 Next Steps

After successful deployment:

1. ✅ Test all features thoroughly
2. ✅ Add monitoring/error tracking
3. ✅ Set up custom domain
4. ✅ Add deployment badge to README
5. ✅ Share on LinkedIn/portfolio
6. ✅ Consider adding analytics (Vercel Analytics, Plausible)

---

**Questions?** Open an issue or check platform documentation.
