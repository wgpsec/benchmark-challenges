/**
 * Browser automation for admin bot
 * Uses simple HTTP requests instead of puppeteer to avoid HTTPS upgrade issues
 */

const http = require('http');
const https = require('https');
const { URL } = require('url');
const querystring = require('querystring');

// Cookie jar to maintain session
let cookies = {};

function parseCookies(setCookieHeaders) {
  if (!setCookieHeaders) return;
  const headers = Array.isArray(setCookieHeaders) ? setCookieHeaders : [setCookieHeaders];
  headers.forEach(header => {
    const parts = header.split(';')[0].split('=');
    if (parts.length >= 2) {
      cookies[parts[0]] = parts.slice(1).join('=');
    }
  });
}

function getCookieHeader() {
  return Object.entries(cookies).map(([k, v]) => `${k}=${v}`).join('; ');
}

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const isHttps = parsedUrl.protocol === 'https:';
    const lib = isHttps ? https : http;

    const requestOptions = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || (isHttps ? 443 : 80),
      path: parsedUrl.pathname + parsedUrl.search,
      method: options.method || 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Cookie': getCookieHeader(),
        ...options.headers
      }
    };

    console.log(`[HTTP] ${requestOptions.method} ${url}`);

    const req = lib.request(requestOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        parseCookies(res.headers['set-cookie']);
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data,
          location: res.headers.location
        });
      });
    });

    req.on('error', reject);

    if (options.body) {
      req.write(options.body);
    }

    req.end();
  });
}

async function visitAndLoginIfNeeded(targetUrl, options) {
  const { appUrl, email, password } = options;

  console.log(`[BROWSER] Starting session (HTTP-based)...`);

  // Reset cookies
  cookies = {};

  try {
    // Step 1: Visit the target URL (which may contain attacker's session ID!)
    console.log(`[BROWSER] Visiting: ${targetUrl}`);
    let response = await makeRequest(targetUrl);

    // Handle redirects
    while (response.statusCode >= 300 && response.statusCode < 400 && response.location) {
      const redirectUrl = new URL(response.location, targetUrl).href;
      console.log(`[BROWSER] Following redirect to: ${redirectUrl}`);
      response = await makeRequest(redirectUrl);
    }

    let currentUrl = targetUrl;
    console.log(`[BROWSER] Status: ${response.statusCode}`);

    // Check if we're on login page (look for email/password inputs)
    const isLoginPage = response.body.includes('name="email"') && response.body.includes('name="password"');

    if (isLoginPage) {
      console.log(`[BROWSER] On login page, authenticating as admin...`);

      // Submit login form
      const loginUrl = new URL('/login', appUrl).href;
      const postData = querystring.stringify({
        email: email,
        password: password
      });

      response = await makeRequest(loginUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Content-Length': Buffer.byteLength(postData)
        },
        body: postData
      });

      console.log(`[BROWSER] Login response status: ${response.statusCode}`);

      // Handle redirect after login
      if (response.statusCode >= 300 && response.statusCode < 400 && response.location) {
        const redirectUrl = new URL(response.location, appUrl).href;
        console.log(`[BROWSER] Following redirect to: ${redirectUrl}`);
        response = await makeRequest(redirectUrl);
        currentUrl = redirectUrl;
      }

      console.log(`[BROWSER] After login, status: ${response.statusCode}`);
    }

    // Get session info
    const sessionId = cookies['session_id'];
    console.log(`[BROWSER] Session cookie: ${sessionId}`);

    return {
      visitedUrl: targetUrl,
      finalUrl: currentUrl,
      pageTitle: 'HTTP-based visit',
      sessionId: sessionId,
      loggedIn: response.body.includes('Dashboard') || response.body.includes('Profile')
    };

  } catch (error) {
    console.error(`[BROWSER] Error:`, error.message);
    throw error;
  }
}

module.exports = { visitAndLoginIfNeeded };
