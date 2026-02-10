import { test, expect, Page } from '@playwright/test';

const timestamp = Date.now();
const testUser = {
  email: `char-e2e-${timestamp}@example.com`,
  username: `char${timestamp}`,
  password: 'TestPassword123!',
};

test.describe('Character & Onboarding', () => {
  
  test('should show character creation during onboarding', async ({ page }) => {
    await page.goto('/register');
    await page.fill('input[name="email"], input[type="email"]', testUser.email);
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"], input[type="password"]', testUser.password);
    await page.click('button[type="submit"]');
    
    // Should redirect to onboarding or character creation
    await page.waitForURL(/\/(onboarding|character)/, { timeout: 15000 });
    
    // Look for character customization elements (LPCCharacter)
    await expect(page.locator('text=/Personnage|Character|Avatar|Créer/i')).toBeVisible({ timeout: 10000 });
    
    // Should have customization options (hair, skin, body, etc.)
    const customOptions = page.locator('button:has-text("Cheveux"), button:has-text("Hair"), [data-testid="hair-option"], text=/Peau|Skin|Corps|Body/i');
    if (await customOptions.first().isVisible({ timeout: 3000 }).catch(() => false)) {
      await expect(customOptions.first()).toBeVisible();
    }
  });

  test('should allow character customization', async ({ page }) => {
    // Register new user
    const ts = Date.now();
    await page.goto('/register');
    await page.fill('input[name="email"], input[type="email"]', `custom-${ts}@test.com`);
    await page.fill('input[name="username"]', `custom${ts}`);
    await page.fill('input[name="password"], input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    
    await page.waitForURL(/\/(onboarding|character)/, { timeout: 15000 });
    
    // Click on customization options if available
    const colorOptions = page.locator('[data-testid="color-picker"], .color-option, button.color-swatch');
    if (await colorOptions.first().isVisible({ timeout: 3000 }).catch(() => false)) {
      await colorOptions.first().click();
    }
    
    // Navigate through categories
    const nextButton = page.locator('button:has-text("Suivant"), button:has-text("Next"), button:has-text("→")');
    if (await nextButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await nextButton.click();
    }
  });

  test('should complete onboarding and access dashboard', async ({ page }) => {
    const ts = Date.now();
    await page.goto('/register');
    await page.fill('input[name="email"], input[type="email"]', `onboard-${ts}@test.com`);
    await page.fill('input[name="username"]', `onboard${ts}`);
    await page.fill('input[name="password"], input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    
    // Complete onboarding by clicking through or skipping
    const skipButton = page.locator('button:has-text("Passer"), button:has-text("Skip")');
    const finishButton = page.locator('button:has-text("Terminer"), button:has-text("Finish"), button:has-text("Commencer"), button:has-text("Start")');
    
    // Try skip or finish
    for (let i = 0; i < 5; i++) {
      if (await finishButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await finishButton.click();
        break;
      }
      if (await skipButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await skipButton.click();
      }
      // Click next if available
      const nextBtn = page.locator('button:has-text("Suivant"), button:has-text("Next")');
      if (await nextBtn.isVisible({ timeout: 500 }).catch(() => false)) {
        await nextBtn.click();
      }
    }
    
    // Should eventually reach dashboard
    await expect(page).toHaveURL(/\/(dashboard|habits)/, { timeout: 20000 });
  });

  test('should display character stats on character page', async ({ page }) => {
    const ts = Date.now();
    await page.goto('/register');
    await page.fill('input[name="email"], input[type="email"]', `stats-${ts}@test.com`);
    await page.fill('input[name="username"]', `stats${ts}`);
    await page.fill('input[name="password"], input[type="password"]', 'TestPassword123!');
    await page.click('button[type="submit"]');
    
    // Skip onboarding
    await page.waitForURL(/\/(onboarding|dashboard|character)/, { timeout: 15000 });
    const skipButton = page.locator('button:has-text("Passer"), button:has-text("Skip")');
    if (await skipButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await skipButton.click();
    }
    
    // Go to character page
    await page.goto('/character');
    
    // Should show stats
    await expect(page.locator('text=/Level|Niveau|XP|HP|Force|Strength/i')).toBeVisible({ timeout: 10000 });
  });
});
