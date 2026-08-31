import os
import time
from playwright.sync_api import sync_playwright

def capture_4k_screenshots():
    images_dir = os.path.join(os.path.dirname(__file__), 'docs', 'images')
    os.makedirs(images_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # 1920x1080 resolution with scale factor 2 (Ultra High-DPI 4K Crisp Screenshots)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2
        )
        page = context.new_page()

        print("1. Capturing Executive Dashboard (http://localhost:8501)...")
        page.goto("http://localhost:8501", wait_until="networkidle")
        time.sleep(5)
        dashboard_path = os.path.join(images_dir, "fig_4_1_dashboard.png")
        page.screenshot(path=dashboard_path, full_page=True)
        print(f"  ✓ Saved crisp Light-Theme dashboard screenshot at {dashboard_path}")

        print("2. Capturing Allocation Simulation View...")
        page.get_by_text("Allocation Simulation").click()
        time.sleep(3)
        
        try:
            submit_btn = page.get_by_role("button", name="Generate Storage Recommendation")
            if submit_btn.is_visible():
                submit_btn.click()
                time.sleep(4)
        except Exception as e:
            print(f"Notice during form submit: {e}")

        allocation_path = os.path.join(images_dir, "fig_4_2_allocation.png")
        page.screenshot(path=allocation_path, full_page=True)
        print(f"  ✓ Saved crisp Light-Theme allocation screenshot at {allocation_path}")

        print("3. Capturing Performance Monitoring View...")
        page.get_by_text("Performance Monitoring").click()
        time.sleep(4)
        monitoring_path = os.path.join(images_dir, "fig_4_3_monitoring.png")
        page.screenshot(path=monitoring_path, full_page=True)
        print(f"  ✓ Saved crisp Light-Theme monitoring screenshot at {monitoring_path}")

        print("4. Capturing Reporting & Evaluation View...")
        page.get_by_text("Reporting & Evaluation").click()
        time.sleep(4)
        reporting_path = os.path.join(images_dir, "fig_4_4_reporting.png")
        page.screenshot(path=reporting_path, full_page=True)
        print(f"  ✓ Saved crisp Light-Theme reporting screenshot at {reporting_path}")

        browser.close()
        print("All 4K high-resolution light-theme screenshots captured successfully!")

if __name__ == "__main__":
    capture_4k_screenshots()
