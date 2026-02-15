from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re
import time

app = Flask(__name__)
CORS(app)

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
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Referer": "https://hdhub4u.fo/"
        }
        
        response = scraper.get(url, headers=headers, timeout=20)
        
        match = re.search(r'href="([^"]+hubcloud\.php\?[^"]+)"', response.text)
        
        if not match:
            match = re.search(r'id="download"[^>]+href="([^"]+)"', response.text)
            
        if not match:
            print("❌ Redirect link nahi mila")
            return {"status": "error", "message": "Redirect Link Not Found"}
            
        next_url = match.group(1).replace("&amp;", "&")
        print(f"✔ Redirecting to: {next_url}")
        
        time.sleep(1)
        headers["Referer"] = url 
        
        final_resp = scraper.get(next_url, headers=headers, timeout=20)
        content = final_resp.text
        
        video_link = re.search(r'(https?://[^"\s\'>]+\.(?:mkv|mp4)[^"\s\'>]*)', content)
        
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

@app.route('/')
def home():
    return jsonify({"status": "online", "message": "HubCloud API is running!"})

@app.route('/solve', methods=['GET'])
def api_handler():
    url = request.args.get('url')
    if not url: 
        return jsonify({"error": "URL missing"}), 400
    return jsonify(solve_hubcloud(url))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
