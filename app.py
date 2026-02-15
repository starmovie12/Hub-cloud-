from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re
import time
app = Flask(__name__)
CORS(app)  # Termux par CORS error hatane ke liye
# --- CONFIGURATION ---
def get_scraper():
    return cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
    )
def solve_hubcloud(url):
    print(f"\n⚡ Processing: {url}")
    scraper = get_scraper()
    
    try:
        # 1. Main Page
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": "[https://hdhub4u.fo/](https://hdhub4u.fo/)"
        }
        
        response = scraper.get(url, headers=headers, timeout=20)
        
        # 2. Find Redirect Link
        # Pattern 1: href="...hubcloud.php?..."
        match = re.search(r'href="([^"]+hubcloud\.php\?[^"]+)"', response.text)
        
        if not match:
            # Pattern 2: id="download" href="..."
            match = re.search(r'id="download"[^>]+href="([^"]+)"', response.text)
            
        if not match:
            print("❌ Redirect link nahi mila")
            return {"status": "error", "message": "Redirect Link Not Found"}
        next_url = match.group(1).replace("&amp;", "&")
        print(f"✔ Redirecting to: {next_url}")
        # 3. Final Step
        time.sleep(1) # Thoda wait
        headers["Referer"] = url 
        
        final_resp = scraper.get(next_url, headers=headers, timeout=20)
        content = final_resp.text
        
        # 4. Extract Final Video Link
        # .mkv ya .mp4 dhundo
        video_link = re.search(r'(https?://[^"\s\'>]+\.(?:mkv|mp4)[^"\s\'>]*)', content)
        
        # Agar direct link na mile to token wala link dhundo (GDFLIX/HubCloud)
        if not video_link:
            video_link = re.search(r'href="([^"]+token=[^"]+)"', content)
            
        if video_link:
            final = video_link.group(1)
            print(f"✅ Link Found: {final}")
            return {"status": "success", "link": final}
        else:
            print("❌ Video Link nahi mila")
            return {"status": "error", "message": "Final Video Link Not Found"}
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return {"status": "error", "message": str(e)}
# --- SERVER ---
@app.route('/solve', methods=['GET'])
def api_handler():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"})
    return jsonify(solve_hubcloud(url))
if __name__ == '__main__':
    # Termux Localhost Port 5000
    print("\n🚀 HubCloud API running on [http://127.0.0.1:5000](http://127.0.0.1:5000)")
    app.run(host='0.0.0.0', port=5000)
