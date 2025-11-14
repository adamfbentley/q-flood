# 🚀 Quick Deployment Checklist

Follow these steps to deploy Q-Flood to free cloud platforms.

## ✅ Pre-Deployment (5 minutes)

- [x] Code pushed to GitHub ✓
- [x] Deployment configs added (Procfile, railway.json, vercel.json) ✓
- [ ] Create Railway account at https://railway.app
- [ ] Create Vercel account at https://vercel.com

---

## 🔧 Backend Deployment - Railway (10 minutes)

### Step 1: Create Railway Project
1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose `q-flood` repository
5. Click "Deploy Now"

### Step 2: Add Environment Variables
In Railway dashboard → Variables tab, add:

```bash
APP_ENV=production
DATABASE_URL=sqlite:///./qflood.db
POSTGRES_DB=qflood
POSTGRES_USER=dev
POSTGRES_PASSWORD=dev
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET_NAME=qflood-data
MINIO_SECURE=false
API_KEY_HASH_SALT=CHANGE_THIS_TO_RANDOM_STRING
REDIS_URL=redis://localhost:6379/0
```

### Step 3: Get Backend URL
- Wait for deployment (3-5 minutes)
- Copy the generated URL from Railway dashboard
- Format: `https://qflood-production.up.railway.app`
- **Save this URL - you'll need it for frontend!**

### Step 4: Test Backend
Visit: `https://your-railway-url.app/docs`
- Should see Swagger UI API documentation
- Test the `/` endpoint - should return welcome message

---

## 🎨 Frontend Deployment - Vercel (5 minutes)

### Step 1: Import Project
1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import `q-flood` from GitHub
4. Set **Root Directory**: `frontend`
5. Framework Preset should auto-detect as "Vite"

### Step 2: Configure Build
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

### Step 3: Add Environment Variable
Click "Environment Variables" and add:

```
VITE_API_URL=https://your-railway-url.app
```
(Replace with your Railway URL from backend step)

### Step 4: Deploy
- Click "Deploy"
- Wait 2-3 minutes for build
- Visit your live site!

---

## ✅ Post-Deployment (5 minutes)

### Test the Full Application

1. **Visit frontend URL** (e.g., https://qflood.vercel.app)
   - [ ] Page loads without errors
   - [ ] Can navigate between pages
   - [ ] No console errors in browser DevTools (F12)

2. **Test API Connection**
   - [ ] Open browser console (F12)
   - [ ] Navigate to different pages
   - [ ] Check Network tab for successful API calls

3. **Verify Backend**
   - [ ] Visit `https://your-railway-url.app/docs`
   - [ ] Try the health check endpoint
   - [ ] Expand and test an API endpoint

### Update GitHub README

Add to the top of README.md:

```markdown
## 🌐 Live Demo

- **Frontend**: https://qflood.vercel.app
- **API Documentation**: https://qflood-production.up.railway.app/docs

*Note: Backend may take 30-60s to wake up on first request (free tier limitation)*
```

Commit and push:
```bash
git add README.md
git commit -m "Add live demo URLs"
git push origin main
```

---

## 🎯 Optional: Custom Domain

### Vercel (Frontend):
1. Project Settings → Domains
2. Add your domain
3. Update DNS records as shown
4. Automatic HTTPS

### Railway (Backend):
1. Settings → Public Networking
2. Add custom domain
3. Update frontend environment variable

---

## 📊 Monitor Your App

### Railway Dashboard:
- **Logs**: Real-time application logs
- **Metrics**: CPU, Memory, Network usage
- **Deployments**: Build history and rollback

### Vercel Dashboard:
- **Analytics**: Page views and performance
- **Deployments**: Build history
- **Logs**: Build and function logs

---

## 🐛 Troubleshooting

### Backend not working?
- Check Railway logs for errors
- Verify all environment variables are set
- Try "Redeploy" in Railway dashboard

### Frontend showing errors?
- Check `VITE_API_URL` environment variable
- Must include full URL with `https://`
- Redeploy after changing env vars

### API calls failing?
- Check browser console for CORS errors
- Backend URL must be accessible
- Railway free tier: check if credits exhausted

---

## 💰 Cost Tracking

### Railway:
- Free: $5 credit/month
- Usage shown in dashboard
- ~500 hours of uptime

### Vercel:
- Free: 100GB bandwidth/month
- Unlimited deployments
- Analytics requires Pro ($20/mo)

---

## 🎉 Success Checklist

- [ ] Backend deployed and accessible at `/docs`
- [ ] Frontend deployed and loading without errors
- [ ] API calls working (check browser console)
- [ ] GitHub README updated with live URLs
- [ ] URLs added to LinkedIn/CV
- [ ] Screenshot taken for portfolio
- [ ] Shared with friends/recruiters!

---

## 📝 Next Steps

1. **Share Your Work**:
   - Add to LinkedIn projects
   - Update CV with live demo link
   - Post on Twitter/social media
   - Share in developer communities

2. **Improve**:
   - Add error monitoring (Sentry)
   - Set up custom domain
   - Add analytics tracking
   - Implement rate limiting

3. **Monitor**:
   - Check logs first week
   - Watch for Railway credit usage
   - Fix any errors that appear

---

## 🆘 Need Help?

- Railway: https://discord.gg/railway
- Vercel: https://vercel.com/docs
- Q-Flood Issues: https://github.com/adamfbentley/q-flood/issues

---

**🎯 Goal**: Get both services deployed within 30 minutes!

Your live URLs will look like:
- Frontend: `https://qflood.vercel.app`
- Backend: `https://qflood-production.up.railway.app`

**Ready? Let's deploy! 🚀**
