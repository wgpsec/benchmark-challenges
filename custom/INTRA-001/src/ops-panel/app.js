const express = require('express');
const fs = require('fs');
const app = express();

const FLAG = process.env.FLAG || fs.readFileSync('/flag.txt', 'utf8').trim();

app.get('/', (req, res) => {
  res.send('<h1>Operations Panel</h1><p>Welcome to internal ops. Navigate to /admin/flag for system status.</p>');
});

app.get('/admin/flag', (req, res) => {
  res.send(`<h1>System Status</h1><p>All systems nominal.</p><p>Verification token: ${FLAG}</p>`);
});

app.listen(8080, '0.0.0.0');
