from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re
import time
import os

app = Flask(__name__)
CORS(app)

# Scraper Setup
def get_scraper():
    return cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )

def solve_hubcloud(url):
    print(f"⚡ Processing: {url}")
    scraper = get_scraper()
    
    try:
        # 1. First Page Load
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": "https://hdhub4u.fo/"
        }
        
        response = scraper.get(url, headers=headers, timeout=20)
        
        # 2. Find Redirect Link
        match = re.search(r'href="([^"]+hubcloud\.php\?[^"]+)"', response.text)
        if not match:
            match = re.search(r'id="download"[^>]+href="([^"]+)"', response.text)
            
        if not match:
            return {"status": "error", "message": "Redirect Link Not Found"}

        next_url = match.group(1).replace("&amp;", "&")
        
        # 3. Final Page Load
        time.sleep(1)
        headers["Referer"] = url 
        final_resp = scraper.get(next_url, headers=headers, timeout=20)
        
        # 4. Extract Video Link
        video_link = re.search(r'(https?://[^"\s\'>]+\.(?:mkv|mp4)[^"\s\'>]*)', final_resp.text)
        
        if not video_link:
            video_link = re.search(r'href="([^"]+token=[^"]+)"', final_resp.text)
            
        if video_link:
            return {"status": "success", "link": video_link.group(1)}
        else:
            return {"status": "error", "message": "Final Video Link Not Found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- ROUTES ---
@app.route('/', methods=['GET'])
def home():
    return "HubCloud API is Running! 🚀"

@app.route('/solve', methods=['GET'])
def api_handler():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL missing"}), 400
    
    result = solve_hubcloud(url)
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
      
