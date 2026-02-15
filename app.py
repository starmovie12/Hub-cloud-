import os
import time
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from DrissionPage import ChromiumPage, ChromiumOptions
from pyvirtualdisplay import Display

app = Flask(__name__)
CORS(app)

# --- 1. VIRTUAL DISPLAY (Render ke liye zaroori) ---
try:
    display = Display(visible=0, size=(1920, 1080))
    display.start()
except:
    pass

# --- 2. BROWSER SETUP ---
def get_browser():
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--headless=new') 
    co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    return ChromiumPage(addr_or_opts=co)

@app.route('/', methods=['GET'])
def home():
    return "HubCloud Solver (DrissionPage Engine) Ready! 🚀"

@app.route('/solve', methods=['GET'])
def api_handler():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"}), 400

    print(f"⚡ Processing: {url}")
    page = None
    try:
        page = get_browser()
        
        # --- STEP 1: OPEN URL ---
        page.get(url)
        
        # Cloudflare Wait (Just a moment...)
        time.sleep(4) 
        
        title = page.title
        print(f"📄 Page Title: {title}")
        
        if "Just a moment" in title or "Access denied" in title:
             return jsonify({"status": "error", "message": "Cloudflare Failed even with Chrome", "debug": title})

        html = page.html

        # --- STEP 2: FIND REDIRECT LINK ---
        # Pattern A: hubcloud.php
        match = re.search(r'href="([^"]+hubcloud\.php\?[^"]+)"', html)
        # Pattern B: Download ID
        if not match: match = re.search(r'id="download"[^>]+href="([^"]+)"', html)
        # Pattern C: Class based
        if not match: match = re.search(r'class="[^"]*btn-success[^"]*"[^>]+href="([^"]+)"', html)

        if not match:
            return jsonify({"status": "error", "message": "Redirect Link Not Found"})

        next_url = match.group(1).replace("&amp;", "&")
        print(f"✔ Redirecting to: {next_url}")

        # --- STEP 3: OPEN NEXT PAGE ---
        page.get(next_url)
        time.sleep(2) # Page load hone ka wait
        
        final_html = page.html
        
        # --- STEP 4: EXTRACT VIDEO ---
        # Direct Video (.mkv, .mp4)
        video_link = re.search(r'(https?://[^"\s\'>]+\.(?:mkv|mp4|avi)[^"\s\'>]*)', final_html)
        
        # Token Link
        if not video_link:
            video_link = re.search(r'href="([^"]+token=[^"]+)"', final_html)
            
        # Button Danger Link
        if not video_link:
             video_link = re.search(r'class="[^"]*btn-danger[^"]*"[^>]+href="([^"]+)"', final_html)

        if video_link:
            final_link = video_link.group(1)
            print(f"✅ FOUND: {final_link}")
            return jsonify({"status": "success", "link": final_link})
        else:
            return jsonify({"status": "error", "message": "Final Video Link Not Found"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        if page:
            page.quit() # Browser band karna zaroori hai

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
