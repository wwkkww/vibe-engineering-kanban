import { test, expect } from "@playwright/test";

test.describe("Authentication Flow", () => {
  test("should redirect unauthenticated user to login page", async ({ page }) => {
    await page.goto("http://localhost:8000/");
    
    // Client-side redirect may take a moment
    await page.waitForURL("**/login");
    
    expect(page.url()).toContain("/login");
    await expect(page.locator("h1")).toContainText("Kanban Studio");
  });

  test("should show error on invalid credentials", async ({ page }) => {
    await page.goto("http://localhost:8000/login");

    await page.fill('input[id="username"]', "user");
    await page.fill('input[id="password"]', "wrongpassword");
    await page.click('button[type="submit"]');

    await expect(page.locator("text=Invalid username or password")).toBeVisible();
  });

  test("should login with correct credentials and redirect to board", async ({ page }) => {
    await page.goto("http://localhost:8000/login");

    await page.fill('input[id="username"]', "user");
    await page.fill('input[id="password"]', "password");
    await page.click('button[type="submit"]');

    // Wait for redirect to board
    await page.waitForURL("http://localhost:8000/");

    // Verify board is visible
    await expect(page.locator("text=Kanban Studio")).toBeVisible();
    await expect(page.locator("text=Backlog")).toBeVisible();
    await expect(page.locator("text=Discovery")).toBeVisible();
    await expect(page.locator("text=In Progress")).toBeVisible();
    await expect(page.locator("text=Review")).toBeVisible();
    await expect(page.locator("text=Done")).toBeVisible();
  });

  test("should show logout button on board", async ({ page }) => {
    await page.goto("http://localhost:8000/login");

    await page.fill('input[id="username"]', "user");
    await page.fill('input[id="password"]', "password");
    await page.click('button[type="submit"]');

    await page.waitForURL("http://localhost:8000/");

    // Verify Sign Out button is visible
    const logoutButton = page.locator('button:has-text("Sign Out")');
    await expect(logoutButton).toBeVisible();
  });

  test("should logout and redirect to login page", async ({ page }) => {
    await page.goto("http://localhost:8000/login");

    // Login
    await page.fill('input[id="username"]', "user");
    await page.fill('input[id="password"]', "password");
    await page.click('button[type="submit"]');

    await page.waitForURL("http://localhost:8000/");

    // Click logout
    const logoutButton = page.locator('button:has-text("Sign Out")');
    await logoutButton.click();

    // Wait for redirect to login
    await page.waitForURL("**/login");
    expect(page.url()).toContain("/login");
  });

  test("should prevent direct access to board without auth", async ({ page, context }) => {
    // Clear all cookies to ensure no auth
    await context.clearCookies();

    // Try to access board directly
    await page.goto("http://localhost:8000/");

    // Should be redirected to login
    await page.waitForURL("**/login", { timeout: 5000 });
    expect(page.url()).toContain("/login");
  });

  test("session should persist on page reload", async ({ page }) => {
    await page.goto("http://localhost:8000/login");

    // Login
    await page.fill('input[id="username"]', "user");
    await page.fill('input[id="password"]', "password");
    await page.click('button[type="submit"]');

    await page.waitForURL("http://localhost:8000/");

    // Reload page
    await page.reload();

    // Should still be on board (session persisted)
    expect(page.url()).toBe("http://localhost:8000/");
    await expect(page.locator("text=Kanban Studio")).toBeVisible();
  });
});
