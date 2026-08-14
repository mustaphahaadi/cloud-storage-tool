import os
import time
from playwright.sync_api import sync_playwright

def capture_screenshots():
    images_dir = os.path.join(os.path.dirname(__file__), 'docs', 'images')
    os.makedirs(images_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1400x950 resolution with Retina 2x scaling for high visual quality
        context = browser.new_context(
            viewport={"width": 1400, "height": 950},
            device_scale_factor=2
        )
        page = context.new_page()

        print("1. Navigating to Executive Dashboard (http://localhost:8501)...")
        page.goto("http://localhost:8501")
        time.sleep(7) # Wait for metrics and Plotly charts to populate completely
        page.screenshot(path=os.path.join(images_dir, "fig_4_1_dashboard.png"))
        print("Captured fig_4_1_dashboard.png (Fully populated dashboard with charts)")

        # 2. Allocation Simulation View
        print("2. Navigating to Allocation Simulation View...")
        page.get_by_text("Allocation Simulation").click()
        time.sleep(3)
        
        # Click Generate Storage Recommendation button to populate metrics & table
        try:
            submit_btn = page.get_by_role("button", name="Generate Storage Recommendation")
            if submit_btn.is_visible():
                submit_btn.click()
                time.sleep(5)
        except Exception as e:
            print(f"Notice during form submit: {e}")
            
        page.screenshot(path=os.path.join(images_dir, "fig_4_2_allocation.png"))
        print("Captured fig_4_2_allocation.png (Fully populated simulation view)")

        # 3. Performance Monitoring View
        print("3. Navigating to Performance Monitoring View...")
        page.get_by_text("Performance Monitoring").click()
        time.sleep(6) # Wait for monitoring charts and metric cards
        page.screenshot(path=os.path.join(images_dir, "fig_4_3_monitoring.png"))
        print("Captured fig_4_3_monitoring.png (Fully populated tier monitoring view)")

        # 4. Reporting & Evaluation View
        print("4. Navigating to Reporting & Evaluation View...")
        page.get_by_text("Reporting & Evaluation").click()
        time.sleep(6) # Wait for historical log dataframes and metrics to render
        page.screenshot(path=os.path.join(images_dir, "fig_4_4_reporting.png"))
        print("Captured fig_4_4_reporting.png (Fully populated audit log analytics view)")

        browser.close()
        print("All high-resolution, fully-populated screenshots successfully captured!")

if __name__ == "__main__":
    capture_screenshots()
