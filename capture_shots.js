const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
  const imagesDir = path.join(__dirname, 'docs', 'images');
  if (!fs.existsSync(imagesDir)) {
    fs.mkdirSync(imagesDir, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1400, height: 950 } });
  const page = await context.newPage();

  console.log('Navigating to http://localhost:8501...');
  await page.goto('http://localhost:8501', { waitUntil: 'networkidle' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(imagesDir, 'fig_4_1_dashboard.png') });
  console.log('Captured fig_4_1_dashboard.png');

  // Allocation Simulation
  await page.click('text=Allocation Simulation');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(imagesDir, 'fig_4_2_allocation.png') });
  console.log('Captured fig_4_2_allocation.png');

  // Performance Monitoring
  await page.click('text=Performance Monitoring');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(imagesDir, 'fig_4_3_monitoring.png') });
  console.log('Captured fig_4_3_monitoring.png');

  // Reporting & Evaluation
  await page.click('text=Reporting & Evaluation');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: path.join(imagesDir, 'fig_4_4_reporting.png') });
  console.log('Captured fig_4_4_reporting.png');

  await browser.close();
  console.log('All 4 system screenshots successfully captured!');
})();
