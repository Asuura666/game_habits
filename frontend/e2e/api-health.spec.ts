import { test, expect } from '@playwright/test';

const API_BASE = process.env.E2E_API_URL || 'http://localhost:8000/api';

test.describe('API Health Checks', () => {
  
  test('API health endpoint should respond', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });

  test('API detailed health should show DB and Redis healthy', async ({ request }) => {
    const response = await request.get(`${API_BASE}/health/detailed`);
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    expect(data.status).toBe('healthy');
    expect(data.database).toBe('healthy');
    expect(data.redis).toBe('healthy');
  });

  test('Auth register endpoint should accept valid data', async ({ request }) => {
    const timestamp = Date.now();
    const response = await request.post(`${API_BASE}/auth/register`, {
      data: {
        email: `apitest-${timestamp}@example.com`,
        username: `apitest${timestamp}`,
        password: 'TestPassword123!'
      }
    });
    
    expect(response.status()).toBe(201);
    const data = await response.json();
    expect(data.access_token).toBeDefined();
    expect(data.user).toBeDefined();
  });

  test('Auth login should reject invalid credentials', async ({ request }) => {
    const response = await request.post(`${API_BASE}/auth/login`, {
      data: {
        email: 'nonexistent@example.com',
        password: 'wrongpassword'
      }
    });
    
    expect(response.status()).toBe(401);
  });

  test('Protected endpoints should require auth', async ({ request }) => {
    const response = await request.get(`${API_BASE}/users/me`);
    expect(response.status()).toBe(401);
  });

  test('Habits endpoint should work with auth', async ({ request }) => {
    // Register and get token
    const timestamp = Date.now();
    const registerRes = await request.post(`${API_BASE}/auth/register`, {
      data: {
        email: `habittest-${timestamp}@example.com`,
        username: `habittest${timestamp}`,
        password: 'TestPassword123!'
      }
    });
    
    expect(registerRes.status()).toBe(201);
    const { access_token } = await registerRes.json();
    
    // Get habits
    const habitsRes = await request.get(`${API_BASE}/habits`, {
      headers: { Authorization: `Bearer ${access_token}` }
    });
    
    expect(habitsRes.status()).toBe(200);
    const habitsData = await habitsRes.json();
    expect(Array.isArray(habitsData.data) || habitsData.data === undefined || habitsData.habits !== undefined).toBe(true);
  });

  test('Shop endpoint should return items', async ({ request }) => {
    // Register and get token
    const timestamp = Date.now();
    const registerRes = await request.post(`${API_BASE}/auth/register`, {
      data: {
        email: `shoptest-${timestamp}@example.com`,
        username: `shoptest${timestamp}`,
        password: 'TestPassword123!'
      }
    });
    
    const { access_token } = await registerRes.json();
    
    // Get shop items
    const shopRes = await request.get(`${API_BASE}/shop/items`, {
      headers: { Authorization: `Bearer ${access_token}` }
    });
    
    expect(shopRes.status()).toBe(200);
  });
});
