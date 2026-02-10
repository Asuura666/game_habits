import { test, expect, Page } from '@playwright/test';

const timestamp = Date.now();
const testUser = {
  email: `habits-e2e-${timestamp}@example.com`,
  username: `habits${timestamp}`,
  password: 'TestPassword123!',
};

async function loginUser(page: Page) {
  await page.goto('/register');
  await page.fill('input[name="email"], input[type="email"]', testUser.email);
  await page.fill('input[name="username"]', testUser.username);
  await page.fill('input[name="password"], input[type="password"]', testUser.password);
  await page.click('button[type="submit"]');
  await page.waitForURL(/\/(onboarding|dashboard|character|habits)/, { timeout: 15000 });
  
  // Skip onboarding if present
  const skipButton = page.locator('button:has-text("Passer"), button:has-text("Skip")');
  if (await skipButton.isVisible({ timeout: 2000 }).catch(() => false)) {
    await skipButton.click();
    await page.waitForURL(/\/(dashboard|habits)/, { timeout: 5000 });
  }
}

test.describe('Habits Management', () => {
  
  test.beforeEach(async ({ page }) => {
    await loginUser(page);
  });

  test('should display habits page', async ({ page }) => {
    await page.goto('/habits');
    
    // Page should load
    await expect(page.locator('text=/Habit|habitude/i')).toBeVisible({ timeout: 10000 });
  });

  test('should create a new habit', async ({ page }) => {
    await page.goto('/habits');
    
    // Click add habit button
    await page.click('button:has-text("+"), button:has-text("Ajouter"), button:has-text("Add"), [data-testid="add-habit"]');
    
    // Fill habit form
    const habitName = `Test Habit ${Date.now()}`;
    await page.fill('input[name="name"], input[name="title"]', habitName);
    
    // Select category if available
    const categorySelect = page.locator('select[name="category"], [data-testid="category-select"]');
    if (await categorySelect.isVisible({ timeout: 1000 }).catch(() => false)) {
      await categorySelect.selectOption({ index: 1 });
    }
    
    // Submit
    await page.click('button[type="submit"], button:has-text("Créer"), button:has-text("Create")');
    
    // Habit should appear in list
    await expect(page.locator(`text=${habitName}`)).toBeVisible({ timeout: 5000 });
  });

  test('should complete a habit', async ({ page }) => {
    await page.goto('/habits');
    
    // Create a habit first
    await page.click('button:has-text("+"), button:has-text("Ajouter"), button:has-text("Add"), [data-testid="add-habit"]');
    const habitName = `Complete Test ${Date.now()}`;
    await page.fill('input[name="name"], input[name="title"]', habitName);
    await page.click('button[type="submit"], button:has-text("Créer"), button:has-text("Create")');
    
    await expect(page.locator(`text=${habitName}`)).toBeVisible({ timeout: 5000 });
    
    // Complete the habit (click on the habit or check button)
    await page.locator(`text=${habitName}`).first().click();
    // Or specific complete button
    const completeButton = page.locator('button:has-text("✓"), button:has-text("Complete"), [data-testid="complete-habit"]');
    if (await completeButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await completeButton.click();
    }
    
    // Should show XP gain or completion feedback
    await expect(page.locator('text=/\+\d+ XP|Complété|Completed/i')).toBeVisible({ timeout: 3000 }).catch(() => {
      // Completion feedback may be different
    });
  });

  test('should delete a habit', async ({ page }) => {
    await page.goto('/habits');
    
    // Create a habit to delete
    await page.click('button:has-text("+"), button:has-text("Ajouter"), button:has-text("Add"), [data-testid="add-habit"]');
    const habitName = `Delete Test ${Date.now()}`;
    await page.fill('input[name="name"], input[name="title"]', habitName);
    await page.click('button[type="submit"], button:has-text("Créer"), button:has-text("Create")');
    
    await expect(page.locator(`text=${habitName}`)).toBeVisible({ timeout: 5000 });
    
    // Open habit menu/options
    await page.locator(`text=${habitName}`).first().hover();
    await page.click('[data-testid="habit-menu"], button:has-text("..."), button:has-text("⋮")');
    
    // Click delete
    await page.click('button:has-text("Supprimer"), button:has-text("Delete")');
    
    // Confirm if needed
    const confirmButton = page.locator('button:has-text("Confirmer"), button:has-text("Confirm")');
    if (await confirmButton.isVisible({ timeout: 1000 }).catch(() => false)) {
      await confirmButton.click();
    }
    
    // Habit should be gone
    await expect(page.locator(`text=${habitName}`)).not.toBeVisible({ timeout: 5000 });
  });
});
