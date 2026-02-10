import { test, expect } from '@playwright/test';

// Unique test user for this run
const timestamp = Date.now();
const testUser = {
  email: `test-e2e-${timestamp}@example.com`,
  username: `teste2e${timestamp}`,
  password: 'TestPassword123!',
};

test.describe('Authentication Flow', () => {
  
  test('should display landing page correctly', async ({ page }) => {
    await page.goto('/');
    
    // Check main elements
    await expect(page.locator('text=HabitQuest')).toBeVisible();
    await expect(page.locator('text=Connexion').or(page.locator('text=Login'))).toBeVisible();
  });

  test('should navigate to register page', async ({ page }) => {
    await page.goto('/');
    
    // Click on register link/button
    await page.click('text=Inscription >> visible=true');
    // or: await page.click('a[href="/register"]');
    
    await expect(page).toHaveURL(/.*register/);
    await expect(page.locator('input[type="email"]').or(page.locator('input[name="email"]'))).toBeVisible();
  });

  test('should register a new user', async ({ page }) => {
    await page.goto('/register');
    
    // Fill registration form
    await page.fill('input[name="email"], input[type="email"]', testUser.email);
    await page.fill('input[name="username"]', testUser.username);
    await page.fill('input[name="password"], input[type="password"]', testUser.password);
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Should redirect to onboarding or dashboard
    await expect(page).toHaveURL(/\/(onboarding|dashboard|character)/);
  });

  test('should login with registered user', async ({ page }) => {
    await page.goto('/login');
    
    // Fill login form
    await page.fill('input[name="email"], input[type="email"]', testUser.email);
    await page.fill('input[name="password"], input[type="password"]', testUser.password);
    
    // Submit
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard or onboarding
    await page.waitForURL(/\/(dashboard|onboarding|character)/, { timeout: 10000 });
  });

  test('should show error on invalid login', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="email"], input[type="email"]', 'invalid@test.com');
    await page.fill('input[name="password"], input[type="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('text=/erreur|invalid|incorrect/i')).toBeVisible({ timeout: 5000 });
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"], input[type="email"]', testUser.email);
    await page.fill('input[name="password"], input[type="password"]', testUser.password);
    await page.click('button[type="submit"]');
    
    await page.waitForURL(/\/(dashboard|onboarding|character)/, { timeout: 10000 });
    
    // Find and click logout button
    await page.click('button:has-text("Déconnexion"), button:has-text("Logout"), [data-testid="logout"]');
    
    // Should redirect to home or login
    await expect(page).toHaveURL(/\/(login)?$/);
  });
});
