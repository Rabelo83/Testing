from playwright.sync_api import sync_playwright
import re

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

        page.goto(url, timeout=60000)

        # Ensure football UI loads
        page.wait_for_selector('a[href*="/football/"]', timeout=60000)
        page.wait_for_timeout(6000)

        team_links = page.query_selector_all('a[href*="/team/"]')

        rows = []

        for link in team_links:
            try:
                row = link.evaluate_handle("el => el.closest('div')")
                text = row.inner_text().strip()

                # ✅ KEEP ONLY ROWS THAT LOOK LIKE STANDINGS
                if re.search(r"\d", text) and len(text) > 15:
                    rows.append(text)

            except:
                continue

        browser.close()

        return {
            "status": "football_page_loaded",
            "team_links_found": len(team_links),
            "rows_found": len(rows),
            "sample_rows": rows[:10]
        }
