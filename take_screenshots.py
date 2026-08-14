import os
import time
from playwright.sync_api import sync_playwright

def capture_screenshots():
    images_dir = os.path.join(os.path.dirname(__file__), 'docs', 'images')
    os.makedirs(images_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 950})
        page = context.new_page()

        print("Navigating to http://localhost:8501...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        time.sleep(3)
        page.screenshot(path=os.path.join(images_dir, "fig_4_1_dashboard.png"))
        print("Captured fig_4_1_dashboard.png")

        # Allocation Simulation View
        page.get_by_text("Allocation Simulation").click()
        time.sleep(3)
        page.screenshot(path=os.path.join(images_dir, "fig_4_2_allocation.png"))
        print("Captured fig_4_2_allocation.png")

        # Performance Monitoring View
        page.get_by_text("Performance Monitoring").click()
        time.sleep(3)
        page.screenshot(path=os.path.join(images_dir, "fig_4_3_monitoring.png"))
        print("Captured fig_4_3_monitoring.png")

        # Reporting & Evaluation View
        page.get_by_text("Reporting & Evaluation").click()
        time.sleep(3)
        page.screenshot(path=os.path.join(images_dir, "fig_4_4_reporting.png"))
        print("Captured fig_4_4_reporting.png")

        browser.close()
        print("All system screenshots successfully captured!")

if __name__ == "__main__":
    capture_screenshots()
