import { test, expect } from '@playwright/test';

// Use production URL for tests
const BASE_URL = 'https://habit.apps.ilanewep.cloud';
const API_URL = 'https://habit.apps.ilanewep.cloud/api';

// Random generators
const randomName = () => {
  const prefixes = ['Shadow', 'Storm', 'Fire', 'Ice', 'Thunder', 'Dark', 'Light', 'Swift', 'Iron', 'Golden'];
  const suffixes = ['blade', 'heart', 'soul', 'fang', 'claw', 'wing', 'star', 'moon', 'sun', 'wolf'];
  return prefixes[Math.floor(Math.random() * prefixes.length)] + 
         suffixes[Math.floor(Math.random() * suffixes.length)] + 
         Math.floor(Math.random() * 100);
};

const CLASSES = ['warrior', 'mage', 'ranger', 'paladin', 'assassin'];
const CLASS_NAMES_FR = ['Guerrier', 'Mage', 'Rôdeur', 'Paladin', 'Assassin'];

test.describe('Character Creation & Onboarding', () => {
  
  test.setTimeout(60000);

  test('should create and verify character via API', async ({ request }) => {
    const timestamp = Date.now();
    const characterName = randomName();
    const classIndex = Math.floor(Math.random() * CLASSES.length);

    // Register
    const registerRes = await request.post(`${API_URL}/auth/register`, {
      data: {
        email: `api-${timestamp}@test.com`,
        username: `api${timestamp}`,
        password: 'TestPassword123!'
      }
    });
    expect(registerRes.ok()).toBeTruthy();
    const { access_token } = await registerRes.json();

    // Create character
    const createRes = await request.post(`${API_URL}/characters/`, {
      headers: { 'Authorization': `Bearer ${access_token}` },
      data: {
        name: characterName,
        character_class: CLASSES[classIndex],
        stats: { strength: 12, intelligence: 10, agility: 10, vitality: 10, luck: 8 },
        avatar_id: `${CLASSES[classIndex]}_m1`
      }
    });
    expect(createRes.ok()).toBeTruthy();
    const character = await createRes.json();
    
    expect(character.name).toBe(characterName);
    expect(character.level).toBe(1);

    // Verify via GET
    const getRes = await request.get(`${API_URL}/characters/me`, {
      headers: { 'Authorization': `Bearer ${access_token}` }
    });
    expect(getRes.ok()).toBeTruthy();
    const fetched = await getRes.json();
    expect(fetched.name).toBe(characterName);

    console.log(`✅ API: Character "${characterName}" (${CLASSES[classIndex]}) created and verified`);
  });

  test('should complete full onboarding flow', async ({ page }) => {
    const timestamp = Date.now();
    const email = `ui-${timestamp}@test.com`;
    const username = `ui${timestamp}`;
    const characterName = randomName();
    const classIndex = Math.floor(Math.random() * CLASS_NAMES_FR.length);
    const gender = Math.random() > 0.5 ? 'Masculin' : 'Féminin';

    console.log(`Creating: ${characterName} (${CLASS_NAMES_FR[classIndex]}, ${gender})`);

    // Go to register on production URL
    await page.goto(`${BASE_URL}/register`);
    
    // Wait for form to load
    await page.locator('input[type="text"]').first().waitFor({ state: 'visible', timeout: 15000 });
    
    // Fill form
    await page.locator('input[type="text"]').first().fill(username);
    await page.locator('input[type="email"]').fill(email);
    await page.locator('input[type="password"]').first().fill('TestPassword123!');
    await page.locator('input[type="password"]').nth(1).fill('TestPassword123!');
    
    // Check the terms checkbox
    await page.locator('input[type="checkbox"]').check();
    
    // Submit
    await page.locator('button[type="submit"]').click();
    
    // Wait for onboarding
    await page.waitForURL('**/onboarding', { timeout: 30000 });

    // Step 1: Name
    await page.locator('input[type="text"]').first().waitFor({ state: 'visible', timeout: 10000 });
    await page.locator('input[type="text"]').first().fill(characterName);
    await page.locator('button:has-text("Continuer")').click();
    
    // Step 2: Class
    await page.locator(`button:has-text("${CLASS_NAMES_FR[classIndex]}")`).waitFor({ state: 'visible', timeout: 10000 });
    await page.locator(`button:has-text("${CLASS_NAMES_FR[classIndex]}")`).click();
    await page.locator('button:has-text("Continuer")').click();
    
    // Step 3: Gender
    await page.locator(`button:has-text("${gender}")`).waitFor({ state: 'visible', timeout: 10000 });
    await page.locator(`button:has-text("${gender}")`).click();
    await page.locator('button:has-text("Continuer")').click();
    
    // Step 4: Confirm
    await expect(page.locator(`text="${characterName}"`)).toBeVisible({ timeout: 10000 });
    await page.locator('button:has-text("Commencer")').click();
    
    // Should reach dashboard
    await page.waitForURL('**/dashboard', { timeout: 30000 });
    
    console.log(`✅ UI: Character "${characterName}" created via onboarding`);
  });

  test('should show character after onboarding', async ({ page }) => {
    const timestamp = Date.now();
    const characterName = randomName();

    // Register
    await page.goto(`${BASE_URL}/register`);
    await page.locator('input[type="text"]').first().waitFor({ state: 'visible', timeout: 15000 });
    await page.locator('input[type="text"]').first().fill(`char${timestamp}`);
    await page.locator('input[type="email"]').fill(`char-${timestamp}@test.com`);
    await page.locator('input[type="password"]').first().fill('TestPassword123!');
    await page.locator('input[type="password"]').nth(1).fill('TestPassword123!');
    await page.locator('input[type="checkbox"]').check();
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/onboarding', { timeout: 30000 });

    // Complete onboarding quickly
    await page.locator('input[type="text"]').first().fill(characterName);
    await page.locator('button:has-text("Continuer")').click();
    await page.locator('button:has-text("Guerrier")').waitFor({ state: 'visible', timeout: 10000 });
    await page.locator('button:has-text("Guerrier")').click();
    await page.locator('button:has-text("Continuer")').click();
    await page.locator('button:has-text("Masculin")').waitFor({ state: 'visible', timeout: 10000 });
    await page.locator('button:has-text("Masculin")').click();
    await page.locator('button:has-text("Continuer")').click();
    await page.locator('button:has-text("Commencer")').click();
    await page.waitForURL('**/dashboard', { timeout: 30000 });

    // Go to character page
    await page.goto(`${BASE_URL}/character`);
    
    // Verify character displayed
    await expect(page.locator(`text="${characterName}"`)).toBeVisible({ timeout: 20000 });
    await expect(page.locator('text=/Niveau|Level/i')).toBeVisible();
    
    console.log(`✅ UI: Character "${characterName}" displayed on /character page`);
  });

  test('should show LPC sprites evolution in onboarding', async ({ page }) => {
    const timestamp = Date.now();

    // Register
    await page.goto(`${BASE_URL}/register`);
    await page.locator('input[type="text"]').first().waitFor({ state: 'visible', timeout: 15000 });
    await page.locator('input[type="text"]').first().fill(`lpc${timestamp}`);
    await page.locator('input[type="email"]').fill(`lpc-${timestamp}@test.com`);
    await page.locator('input[type="password"]').first().fill('TestPassword123!');
    await page.locator('input[type="password"]').nth(1).fill('TestPassword123!');
    await page.locator('input[type="checkbox"]').check();
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/onboarding', { timeout: 30000 });

    // Go to step 3 (appearance)
    await page.locator('input[type="text"]').first().fill('TestHero');
    await page.locator('button:has-text("Continuer")').click();
    await page.locator('button:has-text("Guerrier")').waitFor({ state: 'visible', timeout: 10000 });
    await page.locator('button:has-text("Guerrier")').click();
    await page.locator('button:has-text("Continuer")').click();

    // Check level evolution preview
    await expect(page.locator('text="Niv. 1"')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text="Niv. 10"')).toBeVisible();
    await expect(page.locator('text="Niv. 20"')).toBeVisible();

    // Check gender buttons
    await expect(page.locator('button:has-text("Masculin")')).toBeVisible();
    await expect(page.locator('button:has-text("Féminin")')).toBeVisible();

    console.log('✅ UI: LPC sprites and level evolution displayed correctly');
  });
});
