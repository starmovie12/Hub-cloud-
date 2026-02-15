from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudscraper
import re
import time
import os

app = Flask(__name__)
CORS(app)

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
        # --- STEP 1: LOAD FIRST PAGE ---
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Referer": "https://hdhub4u.fo/"
        }
        
        # Allow redirects true rakha hai taki agar direct video page par bhej de to pakad le
        response = scraper.get(url, headers=headers, allow_redirects=True, timeout=20)
        
        # 🛑 DEBUG CHECK: Agar Cloudflare ne roka hai to pata chal jayega
        page_title_match = re.search(r'<title>(.*?)</title>', response.text)
        page_title = page_title_match.group(1) if page_title_match else "No Title"
        print(f"📄 Page Title: {page_title}")

        if "Just a moment" in page_title or "Access denied" in page_title:
            return {"status": "error", "message": "Cloudflare Blocked IP (Try redeploying)", "title": page_title}

        # --- STEP 2: FIND REDIRECT LINK (3 Patterns) ---
        
        # Pattern A: Standard HubCloud Link
        match = re.search(r'href="([^"]+hubcloud\.php\?[^"]+)"', response.text)
        
        # Pattern B: ID based (aksar 'download' id hoti hai)
        if not match:
            match = re.search(r'id="download"[^>]+href="([^"]+)"', response.text)
            
        # Pattern C: Generic Class based (kabhi kabhi btn-success hota hai)
        if not match:
             match = re.search(r'class="[^"]*btn-success[^"]*"[^>]+href="([^"]+)"', response.text)

        if not match:
            # Agar ab bhi nahi mila, to HTML ka thoda hissa return karo debug ke liye
            return {
                "status": "error", 
                "message": "Redirect Link Not Found (Regex Mismatch)", 
                "html_snippet": response.text[:200]
            }

        next_url = match.group(1).replace("&amp;", "&")
        print(f"✔ Redirect Found: {next_url}")
        
        # --- STEP 3: FINAL PAGE ---
        time.sleep(1) # Thoda saans lene do server ko
        headers["Referer"] = url 
        
        final_resp = scraper.get(next_url, headers=headers, timeout=20)
        content = final_resp.text
        
        # --- STEP 4: EXTRACT VIDEO LINK ---
        # Direct .mkv / .mp4 / .avi
        video_link = re.search(r'(https?://[^"\s\'>]+\.(?:mkv|mp4|avi)[^"\s\'>]*)', content)
        
        # Token Link (GDFLIX/HubCloud Special)
        if not video_link:
            video_link = re.search(r'href="([^"]+token=[^"]+)"', content)
            
        # Kabhi kabhi link 'btn-danger' me hota hai
        if not video_link:
             video_link = re.search(r'class="[^"]*btn-danger[^"]*"[^>]+href="([^"]+)"', content)

        if video_link:
            return {"status": "success", "link": video_link.group(1)}
        else:
            return {
                "status": "error", 
                "message": "Final Video Link Not Found",
                "final_page_title": re.search(r'<title>(.*?)</title>', content).group(1) if re.search(r'<title>(.*?)</title>', content) else "Unknown"
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- SERVER ---
@app.route('/', methods=['GET'])
def home():
    return "HubCloud Solver V2 is Ready! 🚀"

@app.route('/solve', methods=['GET'])
def api_handler():
    url = request.args.get('url')
    if not url: return jsonify({"error": "URL missing"}), 400
    return jsonify(solve_hubcloud(url))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
