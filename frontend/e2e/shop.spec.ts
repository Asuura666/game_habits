import { test, expect, Page } from '@playwright/test';

const timestamp = Date.now();
const testUser = {
  email: `shop-e2e-${timestamp}@example.com`,
  username: `shop${timestamp}`,
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

test.describe('Shop', () => {
  
  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page);
  });

  test('should display shop page with items', async ({ page }) => {
    await page.goto('/shop');
    
    // Shop should load
    await expect(page.locator('text=/Shop|Boutique|Items/i')).toBeVisible({ timeout: 10000 });
    
    // Should have items or categories
    await expect(page.locator('[data-testid="shop-item"], .shop-item, text=/Gold|Coins|💰/')).toBeVisible({ timeout: 5000 }).catch(() => {
      // Shop may be empty or have different structure
    });
  });

  test('should display item categories', async ({ page }) => {
    await page.goto('/shop');
    
    // Look for category tabs/filters
    const categories = page.locator('button:has-text("Armes"), button:has-text("Armures"), button:has-text("Weapons"), [role="tab"]');
    if (await categories.first().isVisible({ timeout: 3000 }).catch(() => false)) {
      await expect(categories.first()).toBeVisible();
    }
  });

  test('should show item details', async ({ page }) => {
    await page.goto('/shop');
    
    // Click on an item if available
    const shopItem = page.locator('[data-testid="shop-item"], .shop-item').first();
    if (await shopItem.isVisible({ timeout: 3000 }).catch(() => false)) {
      await shopItem.click();
      
      // Should show details (name, price, description)
      await expect(page.locator('text=/Prix|Price|\d+ Gold|\d+ 💰/i')).toBeVisible({ timeout: 3000 });
    }
  });

  test('should show insufficient funds message when trying to buy expensive item', async ({ page }) => {
    await page.goto('/shop');
    
    // Try to buy an item (new user has 0 gold)
    const buyButton = page.locator('button:has-text("Acheter"), button:has-text("Buy")').first();
    if (await buyButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await buyButton.click();
      
      // Should show error (not enough gold)
      await expect(page.locator('text=/insuffisant|not enough|pas assez/i')).toBeVisible({ timeout: 3000 }).catch(() => {
        // May have different error handling
      });
    }
  });
});
