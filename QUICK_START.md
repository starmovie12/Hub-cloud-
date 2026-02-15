# 🚀 Quick Deploy - Copy & Paste Commands

## 📁 Files You Need:
1. ✅ app.py (your code - NO CHANGES)
2. ✅ requirements.txt

---

## ⚡ 5-Minute GitHub Upload

```bash
# Step 1: Setup (in Terminal/Command Prompt)
cd Desktop
mkdir hubcloud-api
cd hubcloud-api

# Step 2: Copy your files here (app.py and requirements.txt)

# Step 3: Git commands
git init
git add .
git commit -m "Initial commit"

# Step 4: Create repo on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/hubcloud-api.git
git branch -M main
git push -u origin main
```

---

## 🌐 Render.com Settings

**Copy these EXACT settings:**

| Setting | Value |
|---------|-------|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app` |

---

## 📝 requirements.txt Contents

```
Flask==3.0.0
flask-cors==4.0.0
cloudscraper==1.2.71
requests==2.31.0
gunicorn==21.2.0
```

---

## 🔄 Update Code Later

```bash
# Edit your files, then:
git add .
git commit -m "Updated"
git push origin main
# Render auto-deploys! ✨
```

---

## ✅ Test Your API

```bash
# Replace with your actual Render URL:
curl "https://YOUR-APP.onrender.com/solve?url=TEST_URL"
```

---

## 🎯 Your API Endpoint

```
https://YOUR-APP.onrender.com/solve?url=YOUR_VIDEO_URL
```

**That's it!** 🎉
