from playwright.sync_api import sync_playwright

def scrape_standings(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process"
            ]
        )

        page = browser.new_page(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        )

        # Load page
        page.goto(url, timeout=60000)

        # Give SofaScore time to render (React app)
        page.wait_for_timeout(8000)

        # Try to read page content safely
        try:
            body = page.query_selector("body")
            if not body:
                browser.close()
                return {
                    "status": "error",
                    "message": "Body not found"
                }

            text = body.inner_text()

            browser.close()

            return {
                "status": "page_loaded",
                "text_sample": text[:2000]  # first 2000 chars only
            }

        except Exception as e:
            browser.close()
            return {
                "status": "error",
                "message": str(e)
            }
