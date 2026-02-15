import os
import time
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
from DrissionPage import ChromiumPage, ChromiumOptions
from pyvirtualdisplay import Display

app = Flask(__name__)
CORS(app)

# 🖥️ Virtual Display (Render ke liye zaroori hai)
try:
    display = Display(visible=0, size=(1920, 1080))
    display.start()
except:
    pass

def get_browser():
    co = ChromiumOptions()
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-dev-shm-usage')
    co.set_argument('--headless=new') 
    co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    return ChromiumPage(addr_or_opts=co)

def solve_hubcloud_logic(url):
    page = None
    try:
        print(f"🚀 Opening Real Chrome: {url}")
        page = get_browser()
        
        # 1. Page Load
        page.get(url)
        
        # 🛡️ Cloudflare Wait (Sabse Zaroori)
        time.sleep(5) 
        
        title = page.title
        print(f"📄 Title: {title}")
        
        if "Just a moment" in title or "Access denied" in title:
             # Agar block hua, to page refresh try karo
             print("⚠️ Cloudflare detected, refreshing...")
             page.refresh()
             time.sleep(5)
        
        html = page.html
        
        # 2. Link Extraction Logic (Regex)
        # HubCloud Redirect Link
        match = re.search(r'href="([^"]+hubcloud\.php\?[^"]+)"', html)
        if not match: match = re.search(r'id="download"[^>]+href="([^"]+)"', html)
        if not match: match = re.search(r'class="[^"]*btn-success[^"]*"[^>]+href="([^"]+)"', html)
        
        if match:
            # Agar Redirect link hai, to us par click/visit karo
            next_url = match.group(1).replace("&amp;", "&")
            print(f"✔ Redirect Found: {next_url}")
            
            page.get(next_url)
            time.sleep(4) # Wait for final page
            html = page.html

        # 3. Final Video Link
        video_link = re.search(r'(https?://[^"\s\'>]+\.(?:mkv|mp4|avi)[^"\s\'>]*)', html)
        if not video_link: video_link = re.search(r'href="([^"]+token=[^"]+)"', html)
        
        if video_link:
            return {"status": "success", "link": video_link.group(1)}
        else:
            return {"status": "error", "message": "Link not found in HTML"}

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if page:
            page.quit() # Browser band karna mat bhoolna

@app.route('/', methods=['GET'])
def home():
    return "HubCloud Real-Browser API Running 🚀"

@app.route('/solve', methods=['GET'])
def solve():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"})
    return jsonify(solve_hubcloud_logic(url))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
