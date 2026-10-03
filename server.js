const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = path.join(__dirname, 'public');
const PAYLOAD_PATH = path.join(__dirname, 'data', 'processed', 'dashboard_payload.json');
const DB_PATH = path.join(__dirname, 'data', 'food_delivery.db');

const MIME_TYPES = {
  '.html': 'text/html; charset=UTF-8',
  '.css': 'text/css; charset=UTF-8',
  '.js': 'application/javascript; charset=UTF-8',
  '.json': 'application/json; charset=UTF-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.csv': 'text/csv; charset=UTF-8'
};

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  let pathname = parsedUrl.pathname;

  // CORS Headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // API 1: Dashboard Data Payload
  if (pathname === '/api/dashboard-data' && req.method === 'GET') {
    if (fs.existsSync(PAYLOAD_PATH)) {
      const data = fs.readFileSync(PAYLOAD_PATH, 'utf-8');
      res.writeHead(200, { 'Content-Type': 'application/json; charset=UTF-8' });
      res.end(data);
    } else {
      res.writeHead(404, { 'Content-Type': 'application/json; charset=UTF-8' });
      res.end(JSON.stringify({ error: 'Dashboard payload not generated yet.' }));
    }
    return;
  }

  // API 2: Run Custom SQL Query against SQLite database via Python helper
  if (pathname === '/api/sql-query' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        const { query } = JSON.parse(body);
        if (!query || typeof query !== 'string') {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Invalid SQL query string' }));
          return;
        }

        // Execute via python sqlite3 wrapper
        const pyScript = `import sqlite3, json, pandas as pd; conn = sqlite3.connect(r'${DB_PATH}'); df = pd.read_sql_query('''${query.replace(/'/g, "''")}''', conn); print(df.to_json(orient='records'))`;
        const output = execSync(`python -c "${pyScript}"`, { encoding: 'utf-8' });
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(output);
      } catch (err) {
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: err.message || 'Failed to execute query' }));
      }
    });
    return;
  }

  // Download Power BI Datasets
  if (pathname.startsWith('/api/download/')) {
    const filename = path.basename(pathname);
    const filePath = path.join(__dirname, 'data', 'power_bi', filename);
    if (fs.existsSync(filePath)) {
      res.writeHead(200, {
        'Content-Type': 'text/csv',
        'Content-Disposition': `attachment; filename="${filename}"`
      });
      fs.createReadStream(filePath).pipe(res);
    } else {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      res.end('File not found');
    }
    return;
  }

  // Static File Serving
  if (pathname === '/') pathname = '/index.html';
  let filePath = path.join(PUBLIC_DIR, pathname);

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/html' });
      res.end('<h1>404 Not Found</h1>');
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
});

server.listen(PORT, () => {
  console.log(`=======================================================`);
  console.log(` FOOD DELIVERY OPERATIONS INTELLIGENCE SERVER STARTED `);
  console.log(` Access Dashboard at: http://localhost:${PORT}`);
  console.log(`=======================================================`);
});
