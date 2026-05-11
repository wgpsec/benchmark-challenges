/**
 * Browser automation for admin bot
 *
 * This bot simulates an admin user visiting malicious URLs.
 * The key challenge is making the session cookie available cross-origin
 * to enable the CORS attack scenario.
 */

const puppeteer = require('puppeteer');

async function visitUrlAsAdmin(targetUrl, options) {
  const { apiUrl, email, password } = options;

  console.log(`[BROWSER] Starting browser session...`);

  const browser = await puppeteer.launch({
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-web-security',
      '--user-data-dir=/tmp/chrome-profile',
      '--allow-running-insecure-content',
      '--disable-features=IsolateOrigins,site-per-process,SameSiteByDefaultCookies,CookiesWithoutSameSiteMustBeSecure',
    ]
  });

  // Create a browser context for better cookie handling
  const context = browser.defaultBrowserContext();

  // Override permissions to allow cross-origin
  await context.overridePermissions(apiUrl, []);

  const page = await browser.newPage();

  // Enable logging
  page.on('console', msg => console.log(`[PAGE CONSOLE] ${msg.text()}`));
  page.on('request', req => {
    console.log(`[PAGE REQUEST] ${req.method()} ${req.url()}`);
  });

  try {
    // Step 1: Login to API
    console.log(`[BROWSER] Logging in as admin...`);

    await page.goto(`${apiUrl}/`, { waitUntil: 'networkidle0' });

    // Perform login via API
    const loginResult = await page.evaluate(async (email, password) => {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        credentials: 'include'
      });
      return await res.json();
    }, email, password);

    console.log(`[BROWSER] Login result:`, loginResult);

    if (!loginResult.user) {
      throw new Error('Login failed');
    }

    console.log(`[BROWSER] Logged in as: ${loginResult.user.email}`);

    // Get all cookies
    const cookies = await page.cookies();
    console.log(`[BROWSER] Cookies after login:`, cookies.map(c => `${c.name}=${c.value.substring(0,20)}...`));

    // Verify we have a session by checking profile
    const profileCheck = await page.evaluate(async () => {
      const res = await fetch('/api/profile', { credentials: 'include' });
      return await res.json();
    });

    console.log(`[BROWSER] Profile check - Role: ${profileCheck.profile?.role}`);
    console.log(`[BROWSER] Profile check - Flag present: ${!!profileCheck.profile?.flag}`);

    // Get the session cookie value for injection into the exploit page
    const sessionCookie = cookies.find(c => c.name === 'connect.sid');

    // Step 2: Visit the attacker's URL
    // Pass the session ID as a URL parameter so the exploit page can use it
    // The session ID is extracted from the cookie value (format: s:SESSION_ID.SIGNATURE)
    let exploitUrl = targetUrl;
    if (sessionCookie) {
      // The cookie value is URL-encoded, decode it first
      const cookieValue = decodeURIComponent(sessionCookie.value);
      // Extract just the session ID (the part between "s:" and ".")
      let sessionId = cookieValue;
      if (sessionId.startsWith('s:')) {
        sessionId = sessionId.substring(2).split('.')[0];
      }

      const separator = targetUrl.includes('?') ? '&' : '?';
      exploitUrl = `${targetUrl}${separator}cookie=${encodeURIComponent(sessionId)}`;
      console.log(`[BROWSER] Passing session ID to exploit page: ${sessionId.substring(0, 10)}...`);
    }

    console.log(`[BROWSER] Visiting attacker URL: ${exploitUrl}`);

    await page.goto(exploitUrl, {
      waitUntil: 'networkidle0',
      timeout: 30000
    });

    // Wait for any JavaScript to execute
    await new Promise(resolve => setTimeout(resolve, 5000));

    const finalUrl = page.url();
    const pageTitle = await page.title();

    console.log(`[BROWSER] Final URL: ${finalUrl}`);
    console.log(`[BROWSER] Page title: ${pageTitle}`);

    await browser.close();

    return {
      visited: targetUrl,
      finalUrl,
      pageTitle,
      adminEmail: email
    };

  } catch (error) {
    console.error(`[BROWSER] Error:`, error);
    await browser.close();
    throw error;
  }
}

module.exports = { visitUrlAsAdmin };
