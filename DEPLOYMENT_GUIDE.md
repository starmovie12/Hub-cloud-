# 🚀 Complete Deployment Guide - Flask HubCloud API

## 📋 Prerequisites
- GitHub account
- Render.com account (free tier works)
- Git installed on your computer

---

## 🔧 STEP 1: Create GitHub Repository

### Option A: Using GitHub Website (Easiest)

1. **Go to GitHub:**
   - Visit: https://github.com
   - Click the **"+"** icon (top right) → **"New repository"**

2. **Repository Settings:**
   - Repository name: `hubcloud-api` (or any name you want)
   - Description: `Flask API for HubCloud video link extraction`
   - Select: **Public** or **Private**
   - ❌ DO NOT check "Add a README file"
   - Click **"Create repository"**

3. **You'll see a page with commands - SAVE IT, we'll use those commands below**

---

### Option B: Using Command Line (Git Bash/Terminal)

```bash
# 1. Navigate to where you want to create the project folder
cd Desktop  # or any location

# 2. Create project directory
mkdir hubcloud-api
cd hubcloud-api

# 3. Copy your files here (app.py and requirements.txt)
# Place both files in this folder

# 4. Initialize Git
git init

# 5. Add files
git add .

# 6. Commit files
git commit -m "Initial commit: HubCloud API"

# 7. Create repository on GitHub (replace YOUR_USERNAME)
# Go to github.com and create a new empty repository first
# Then run these commands:

git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hubcloud-api.git
git push -u origin main
```

---

## 📤 STEP 2: Upload Files to GitHub

### If you used Option A (Website):

**On your computer:**

```bash
# 1. Open Terminal/Command Prompt/Git Bash

# 2. Navigate to Desktop (or where you want to work)
cd Desktop

# 3. Clone the repository you just created (replace YOUR_USERNAME)
git clone https://github.com/YOUR_USERNAME/hubcloud-api.git

# 4. Enter the folder
cd hubcloud-api

# 5. Copy your app.py and requirements.txt files into this folder
# (Manually copy-paste the files here)

# 6. Add files to Git
git add app.py requirements.txt

# 7. Commit the files
git commit -m "Add Flask app and requirements"

# 8. Push to GitHub
git push origin main
```

**Enter your GitHub credentials when prompted**

---

## 🔍 STEP 3: Verify Files on GitHub

1. Go to your repository: `https://github.com/YOUR_USERNAME/hubcloud-api`
2. You should see:
   - ✅ `app.py`
   - ✅ `requirements.txt`
3. If both files are visible → SUCCESS! ✨

---

## 🌐 STEP 4: Deploy to Render.com

### 1. Create Render Account
- Go to: https://render.com
- Sign up (use GitHub login for easier integration)

### 2. Create New Web Service

1. **Dashboard:**
   - Click **"New +"** button (top right)
   - Select **"Web Service"**

2. **Connect Repository:**
   - If first time: Click **"Connect GitHub"** and authorize Render
   - Find your repository: `hubcloud-api`
   - Click **"Connect"**

3. **Configuration:**

   | Field | Value |
   |-------|-------|
   | **Name** | `hubcloud-api` (or any name) |
   | **Region** | Choose closest to you |
   | **Branch** | `main` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn app:app` |

4. **Environment:**
   - Instance Type: **Free**
   - Click **"Create Web Service"**

---

## ⚙️ STEP 5: Fix Start Command Issue

### Problem: Render needs Gunicorn

Your app uses `app.run()` but Render needs `gunicorn`. We have 2 solutions:

### ✅ Solution 1: Add Gunicorn (Recommended)

**Update your `requirements.txt`:**

```bash
# On your computer, edit requirements.txt and add this line:
gunicorn==21.2.0
```

**Then update GitHub:**

```bash
# In your terminal (in the project folder):
git add requirements.txt
git commit -m "Add gunicorn"
git push origin main
```

**Render will auto-deploy! ✨**

---

### Solution 2: Use Python directly (Not recommended for production)

**In Render Dashboard:**
- Start Command: `python app.py`

**⚠️ Warning:** This works but isn't production-ready

---

## 🎯 STEP 6: Get Your API URL

1. **Wait for Deployment:**
   - Render dashboard will show "Building..." then "Live"
   - Takes 2-5 minutes

2. **Your API URL:**
   ```
   https://hubcloud-api.onrender.com
   ```
   (Your actual URL will be shown in Render dashboard)

3. **Test it:**
   ```bash
   curl "https://hubcloud-api.onrender.com/solve?url=YOUR_TEST_URL"
   ```

---

## 📝 Complete Commands Reference

### Initial Setup (Do Once)

```bash
# 1. Create folder
mkdir hubcloud-api
cd hubcloud-api

# 2. Create your files
# Copy app.py here
# Copy requirements.txt here

# 3. Initialize Git
git init
git add .
git commit -m "Initial commit"

# 4. Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/hubcloud-api.git
git branch -M main
git push -u origin main
```

### Update Code (Do When Making Changes)

```bash
# 1. Edit your files (app.py or requirements.txt)

# 2. Save and commit
git add .
git commit -m "Description of changes"
git push origin main

# 3. Render will auto-deploy! ✨
```

---

## 🔧 Render Configuration Summary

Copy these exact settings in Render:

```
Name: hubcloud-api
Region: (Your choice)
Branch: main
Runtime: Python 3

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn app:app

Environment Variables: (None needed)
Instance Type: Free
```

---

## ✅ Final Checklist

Before deploying, verify:

- [ ] `app.py` exists and has no syntax errors
- [ ] `requirements.txt` includes all packages (Flask, flask-cors, cloudscraper, gunicorn)
- [ ] Files are pushed to GitHub (visible in repository)
- [ ] Render connected to correct GitHub repository
- [ ] Start command is `gunicorn app:app`
- [ ] Deployment shows "Live" status in Render

---

## 🚨 Common Issues & Solutions

### Issue 1: "Module not found" error
**Solution:** Add missing package to `requirements.txt`

```bash
# Edit requirements.txt, add the package
git add requirements.txt
git commit -m "Fix dependencies"
git push origin main
```

### Issue 2: "Port already in use"
**Solution:** Already handled! Render automatically assigns the correct port

### Issue 3: "Build failed"
**Check:**
1. requirements.txt syntax (no typos)
2. Render build logs (click "Logs" tab)
3. Python version compatibility

### Issue 4: "Start command failed"
**Solution:** Make sure you added `gunicorn==21.2.0` to requirements.txt

### Issue 5: API returns 404
**Check:**
- URL format: `https://your-api.onrender.com/solve?url=...`
- Endpoint is `/solve` not `/`
- Query parameter is `url=...`

---

## 📞 Testing Your Deployed API

### Test 1: Health Check
```bash
curl https://your-api.onrender.com/solve
```
Expected: `{"error": "URL missing"}`

### Test 2: Real Request
```bash
curl "https://your-api.onrender.com/solve?url=https://example.com/video"
```
Expected: JSON response with status

### Test 3: Browser
Open in browser:
```
https://your-api.onrender.com/solve?url=https://example.com/video
```

---

## 🔒 Security Notes

1. **Rate Limiting:** Render free tier has limits (check dashboard)
2. **API Key:** Consider adding authentication for production
3. **CORS:** Currently allows all origins (good for testing, restrict for production)

---

## 📊 Monitoring

### Render Dashboard:
- **Logs:** Click "Logs" to see print statements
- **Metrics:** View request count and response times
- **Deploys:** See deployment history

### What to Watch:
- Response times (should be < 5s)
- Error rate (should be low)
- Build time (should be < 3 min)

---

## 🔄 Updating Your Code

Every time you change code:

```bash
# 1. Edit files locally
nano app.py  # or use any editor

# 2. Test locally
python app.py

# 3. Commit and push
git add .
git commit -m "Updated feature X"
git push origin main

# 4. Render auto-deploys in 2-3 minutes ✨
```

---

## 🎉 Success!

Your API is now live at:
```
https://hubcloud-api.onrender.com/solve?url=YOUR_URL
```

### Next Steps:
1. Share the API URL with your team
2. Add it to your app/website
3. Monitor usage in Render dashboard
4. Update code via Git whenever needed

---

## 📚 Quick Reference

| Action | Command |
|--------|---------|
| Clone repo | `git clone https://github.com/YOU/hubcloud-api.git` |
| Make changes | Edit files with any text editor |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push to GitHub | `git push origin main` |
| Check status | `git status` |
| View logs (Render) | Dashboard → Logs tab |

---

**Need help?** Check Render logs first - they show exactly what went wrong!
