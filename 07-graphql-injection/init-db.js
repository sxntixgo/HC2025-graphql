const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

// Database file path
const dbPath = path.join(__dirname, 'data', 'challenge.db');

// Ensure data directory exists
const dataDir = path.dirname(dbPath);
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

// Remove existing database if it exists
if (fs.existsSync(dbPath)) {
  fs.unlinkSync(dbPath);
}

// Create database with write access for initialization
const db = new sqlite3.Database(dbPath);

console.log('Initializing database...');

db.serialize(() => {
  db.run(`
    CREATE TABLE users (
      id INTEGER PRIMARY KEY,
      username TEXT,
      email TEXT,
      role TEXT
    )
  `);

  db.run(`
    CREATE TABLE documents (
      id INTEGER PRIMARY KEY,
      title TEXT,
      content TEXT,
      confidential INTEGER,
      internal_ref TEXT,
      debug_info TEXT,
      user_id INTEGER
    )
  `);

  const users = [
    [1, 'john_doe', 'john@company.com', 'employee'],
    [2, 'jane_smith', 'jane@company.com', 'manager'],
    [3, 'admin_user', 'admin@company.com', 'admin']
  ];

  // Use placeholder for FLAG during build
  const flagValue = process.env.FLAG || 'FLAG_PLACEHOLDER';

  const documents = [
    [1, 'Public Document', 'This is public content', 0, 'DOC_001', 'Public access allowed', 1],
    [2, 'Confidential Report', 'Secret business data', 1, 'SECRET_002', flagValue, 3],
    [3, 'User Manual', 'How to use the system', 0, 'DOC_003', 'General documentation', 2],
    [4, 'Internal Memo', 'Company internal communication', 1, 'MEMO_004', 'Internal use only', 2]
  ];

  users.forEach(user => {
    db.run('INSERT INTO users VALUES (?, ?, ?, ?)', user, (err) => {
      if (err) console.error('Error inserting user:', err);
    });
  });

  documents.forEach(document => {
    db.run('INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?)', document, (err) => {
      if (err) console.error('Error inserting document:', err);
    });
  });
});

db.close((err) => {
  if (err) {
    console.error('Error closing database:', err);
    process.exit(1);
  }

  console.log('Database initialized successfully at:', dbPath);

  // Make file read-only at OS level (444 = r--r--r--)
  try {
    fs.chmodSync(dbPath, 0o444);
    console.log('Database file set to read-only mode');
  } catch (chmodErr) {
    console.error('Warning: Could not set read-only permissions:', chmodErr.message);
  }
});
