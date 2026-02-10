import { test, expect, Page } from '@playwright/test';

const timestamp = Date.now();
const testUser = {
  email: `dashboard-e2e-${timestamp}@example.com`,
  username: `dash${timestamp}`,
  password: 'TestPassword123!',
};

async function registerAndLogin(page: Page) {
  await page.goto('/register');
  await page.fill('input[name="email"], input[type="email"]', testUser.email);
  await page.fill('input[name="username"]', testUser.username);
  await page.fill('input[name="password"], input[type="password"]', testUser.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(onboarding|dashboard|character)/, { timeout: 15000 });
}

test.describe('Dashboard', () => {
  
  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page);
  });

  test('should display user stats on dashboard', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should show level/XP info
    await expect(page.locator('text=/Niveau|Level|XP/i')).toBeVisible({ timeout: 10000 });
  });

  test('should display streak information', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should show streak
    await expect(page.locator('text=/streak|série|🔥/i')).toBeVisible({ timeout: 10000 });
  });

  test('should navigate to different sections', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Navigate to habits
    await page.click('a[href="/habits"], button:has-text("Habits"), nav >> text=Habitudes');
    await expect(page).toHaveURL(/.*habits/);
    
    // Navigate to shop
    await page.goto('/dashboard');
    await page.click('a[href="/shop"], button:has-text("Shop"), nav >> text=Boutique');
    await expect(page).toHaveURL(/.*shop/);
    
    // Navigate to stats
    await page.goto('/dashboard');
    await page.click('a[href="/stats"], button:has-text("Stats"), nav >> text=Statistiques');
    await expect(page).toHaveURL(/.*stats/);
  });
});
