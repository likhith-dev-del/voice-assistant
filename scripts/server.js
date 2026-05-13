// server.js
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const app = express();
const db = new sqlite3.Database('./ria.db');

// Create tables
db.serialize(() => {
  db.run(`CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )`);
});

// API Endpoints
app.post('/signup', express.json(), (req, res) => {
  const { email, password } = req.body;
  db.run(
    'INSERT INTO users (email, password) VALUES (?, ?)',
    [email, password],
    function(err) {
      if (err) return res.status(400).json({ error: err.message });
      res.json({ success: true, userId: this.lastID });
    }
  );
});

app.post('/login', express.json(), (req, res) => {
  const { email, password } = req.body;
  db.get(
    'SELECT * FROM users WHERE email = ? AND password = ?',
    [email, password],
    (err, row) => {
      if (err || !row) return res.status(401).json({ error: 'Invalid credentials' });
      res.json({ success: true, user: row });
    }
  );
});

app.listen(3000, () => console.log('Server running on port 3000'));
