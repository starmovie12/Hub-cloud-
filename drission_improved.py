from DrissionPage import ChromiumPage, ChromiumOptions
from pyvirtualdisplay import Display
from flask import Flask, request, jsonify
import time
import logging
from typing import Optional, Dict, Any

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# --- 1. Virtual Display Setup ---
display = None
try:
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    logger.info("✓ Virtual display started successfully")
except Exception as e:
    logger.error(f"✗ Display initialization failed: {e}")

# --- 2. Enhanced Browser Setup ---
def get_page() -> Optional[ChromiumPage]:
    """
    Creates and returns a configured ChromiumPage instance with anti-detection measures.
    Returns None if initialization fails.
    """
    try:
        logger.info("Initializing browser...")
        co = ChromiumOptions()
        
        # Security & Performance
        co.set_argument('--no-sandbox')
        co.set_argument('--disable-dev-shm-usage')
        co.set_argument('--disable-gpu')
        
        # Anti-Detection
        co.set_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--disable-infobars')
        co.set_argument('--window-size=1920,1080')
        
        # Additional stealth settings
        co.set_argument('--disable-web-security')
        co.set_argument('--disable-features=IsolateOrigins,site-per-process')
        
        page = ChromiumPage(addr_or_opts=co)
        logger.info("✓ Browser initialized successfully")
        return page
        
    except Exception as e:
        logger.error(f"✗ Browser initialization failed: {e}")
        return None

def wait_for_page_load(page: ChromiumPage, timeout: int = 30) -> bool:
    """
    Waits for page to be in ready state.
    Returns True if successful, False otherwise.
    """
    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if page.states.is_alive:
                logger.info(f"✓ Page loaded: {page.title}")
                return True
            time.sleep(0.5)
        logger.warning(f"⚠ Page load timeout after {timeout}s")
        return False
    except Exception as e:
        logger.error(f"✗ Error checking page state: {e}")
        return False

def handle_cloudflare_challenge(page: ChromiumPage, max_attempts: int = 3) -> bool:
    """
    Detects and attempts to solve Cloudflare challenges.
    Returns True if challenge was handled, False otherwise.
    """
    try:
        title_lower = page.title.lower()
        page_text_lower = page.html.lower()
        
        # Detection patterns
        cf_patterns = [
            "challenge" in title_lower,
            "just a moment" in title_lower,
            "checking your browser" in title_lower,
            "access denied" in title_lower,
            "cloudflare" in page_text_lower
        ]
        
        if not any(cf_patterns):
            logger.info("✓ No Cloudflare challenge detected")
            return True
            
        logger.warning("⚠ Cloudflare challenge detected, attempting to solve...")
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Attempt {attempt}/{max_attempts}")
            
            # Wait for challenge to render
            time.sleep(5)
            
            # Method 1: Look for checkbox in shadow DOM
            try:
                checkbox = page.ele('@type=checkbox', timeout=3)
                if checkbox:
                    logger.info("Found checkbox, clicking...")
                    checkbox.click()
                    time.sleep(10)
                    
                    # Verify if challenge was solved
                    if "access denied" not in page.title.lower() and "challenge" not in page.title.lower():
                        logger.info("✓ Challenge solved successfully")
                        return True
            except Exception as e:
                logger.debug(f"Checkbox method failed: {e}")
            
            # Method 2: Look for verify button
            try:
                verify_btn = page.ele('text:Verify you are human', timeout=3)
                if verify_btn:
                    logger.info("Found verify button, clicking...")
                    verify_btn.click()
                    time.sleep(10)
                    
                    if "access denied" not in page.title.lower():
                        logger.info("✓ Challenge solved via verify button")
                        return True
            except Exception as e:
                logger.debug(f"Verify button method failed: {e}")
            
            # Method 3: Try refresh
            if attempt < max_attempts:
                logger.info("Refreshing page...")
                page.refresh()
                time.sleep(8)
        
        logger.error("✗ Failed to solve Cloudflare challenge")
        return False
        
    except Exception as e:
        logger.error(f"✗ Error handling Cloudflare: {e}")
        return False

def find_download_links(page: ChromiumPage) -> Dict[str, Any]:
    """
    Searches for HubDrive/HubCloud links using multiple strategies.
    Returns dict with status and link if found.
    """
    try:
        logger.info("Searching for download links...")
        
        # Strategy 1: Direct href search (case-insensitive)
        strategies = [
            # HubDrive patterns
            ('tag:a@@href:hubdrive', 'HubDrive (direct)'),
            ('tag:a@@href:HubDrive', 'HubDrive (capitalized)'),
            ('tag:a@@href*=hubdrive', 'HubDrive (contains)'),
            
            # HubCloud patterns
            ('tag:a@@href:hubcloud', 'HubCloud (direct)'),
            ('tag:a@@href:HubCloud', 'HubCloud (capitalized)'),
            ('tag:a@@href*=hubcloud', 'HubCloud (contains)'),
            
            # Generic download button
            ('tag:a@@text():Download', 'Download button'),
            ('tag:button@@text():Download', 'Download button (button tag)'),
            ('@id:download', 'ID: download'),
            ('@class:download', 'Class: download'),
        ]
        
        for selector, description in strategies:
            try:
                logger.info(f"Trying: {description} - {selector}")
                element = page.ele(selector, timeout=2)
                
                if element:
                    link = element.attr('href')
                    if link:
                        logger.info(f"✓ Found link via {description}: {link}")
                        return {
                            "status": "success",
                            "link": link,
                            "source": description,
                            "method": selector
                        }
            except Exception as e:
                logger.debug(f"Strategy '{description}' failed: {e}")
                continue
        
        # Strategy 2: Search all links containing keywords
        logger.info("Searching all links for keywords...")
        all_links = page.eles('tag:a')
        logger.info(f"Found {len(all_links)} total links on page")
        
        keywords = ['hubdrive', 'hubcloud', 'download', 'gdflix']
        
        for link_elem in all_links:
            try:
                href = link_elem.attr('href')
                text = link_elem.text.lower() if link_elem.text else ''
                
                if href:
                    href_lower = href.lower()
                    for keyword in keywords:
                        if keyword in href_lower or keyword in text:
                            logger.info(f"✓ Found link with keyword '{keyword}': {href}")
                            return {
                                "status": "success",
                                "link": href,
                                "source": f"Keyword match: {keyword}",
                                "method": "full_scan"
                            }
            except:
                continue
        
        logger.warning("✗ No download links found")
        return {
            "status": "fail",
            "message": "No download links found",
            "page_title": page.title,
            "final_url": page.url,
            "total_links_scanned": len(all_links)
        }
        
    except Exception as e:
        logger.error(f"✗ Error searching for links: {e}")
        return {
            "status": "error",
            "message": f"Link search failed: {str(e)}"
        }

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Nuclear Bot is Live!",
        "endpoints": {
            "/solve": "GET with ?url=<target_url>"
        }
    })

@app.route('/solve', methods=['GET'])
def solve():
    url = request.args.get('url')
    
    if not url:
        logger.warning("Request received without URL parameter")
        return jsonify({
            "status": "error",
            "message": "URL parameter is required"
        }), 400
    
    logger.info(f"\n{'='*60}")
    logger.info(f"NEW REQUEST: {url}")
    logger.info(f"{'='*60}")
    
    page = None
    
    try:
        # Step 1: Initialize browser
        logger.info("[1/5] Initializing browser...")
        page = get_page()
        if not page:
            return jsonify({
                "status": "error",
                "message": "Browser initialization failed"
            }), 500
        
        # Step 2: Navigate to URL
        logger.info(f"[2/5] Navigating to: {url}")
        page.get(url, timeout=30)
        
        # Step 3: Wait for page load
        logger.info("[3/5] Waiting for page to load...")
        if not wait_for_page_load(page):
            return jsonify({
                "status": "error",
                "message": "Page load timeout"
            }), 500
        
        # Initial wait for dynamic content
        time.sleep(5)
        
        # Step 4: Handle Cloudflare
        logger.info("[4/5] Checking for Cloudflare...")
        if not handle_cloudflare_challenge(page):
            return jsonify({
                "status": "error",
                "message": "Failed to bypass Cloudflare protection",
                "page_title": page.title
            }), 403
        
        # Additional wait after challenge
        time.sleep(3)
        
        # Step 5: Extract links
        logger.info("[5/5] Extracting download links...")
        result = find_download_links(page)
        
        logger.info(f"Result: {result.get('status', 'unknown')}")
        logger.info(f"{'='*60}\n")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"✗ CRITICAL ERROR: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }), 500
        
    finally:
        if page:
            try:
                logger.info("Closing browser...")
                page.quit()
                logger.info("✓ Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")

if __name__ == '__main__':
    logger.info("\n" + "="*60)
    logger.info("🚀 NUCLEAR BOT STARTING")
    logger.info("="*60 + "\n")
    app.run(host='0.0.0.0', port=10000, debug=False)
