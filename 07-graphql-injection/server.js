const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema } = require('graphql');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = express();

// Database file path - use read-only database
const dbPath = path.join(__dirname, 'data', 'challenge.db');

// Check if database file exists
if (!fs.existsSync(dbPath)) {
  console.error('ERROR: Database file not found at:', dbPath);
  console.error('Please run: node init-db.js');
  process.exit(1);
}

// Open database in read-only mode
const db = new sqlite3.Database(dbPath, sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error('Error opening database in read-only mode:', err);
    process.exit(1);
  }
  console.log('Database opened in READ-ONLY mode');
});

// Update FLAG in memory if needed (for runtime flag injection)
if (process.env.FLAG && process.env.FLAG !== 'FLAG_PLACEHOLDER') {
  console.log('Note: FLAG provided at runtime, but database is read-only');
  console.log('To update FLAG in database, run: FLAG=your_flag node init-db.js');
}

const schema = buildSchema(`
  type User {
    id: Int
    username: String
    email: String
    role: String
    documents: [Document]
  }

  type Document {
    id: Int
    title: String
    content: String
    confidential: Boolean
    internal_ref: String
    debug_info: String
    owner: User
  }

  type Query {
    users: [User]
    user(id: Int!): User
    documents: [Document]
    document(id: Int!): Document
    searchUsers(username: String!): [User]
  }
`);


// Helper function for user documents
const getUserDocuments = (userId) => {
  return new Promise((resolve, reject) => {
    db.all('SELECT * FROM documents WHERE user_id = ? AND confidential = 0', [userId], async (err, rows) => {
      if (err) {
        reject(err);
      } else {
        try {
          const docsWithOwners = await Promise.all(
            rows.map(async (doc) => {
              const owner = await getDocumentOwner(doc.user_id);
              return { ...doc, confidential: !!doc.confidential, owner };
            })
          );
          resolve(docsWithOwners);
        } catch (error) {
          reject(error);
        }
      }
    });
  });
};

// Helper function for document owner
const getDocumentOwner = (userId) => {
  return new Promise((resolve, reject) => {
    db.get('SELECT * FROM users WHERE id = ?', [userId], (err, row) => {
      if (err) reject(err);
      else resolve(row);
    });
  });
};

const root = {
  users: () => {
    return new Promise((resolve, reject) => {
      db.all('SELECT * FROM users', async (err, users) => {
        if (err) {
          reject(err);
        } else {
          try {
            const usersWithDocs = await Promise.all(
              users.map(async (user) => {
                const documents = await getUserDocuments(user.id);
                return { ...user, documents };
              })
            );
            resolve(usersWithDocs);
          } catch (error) {
            reject(error);
          }
        }
      });
    });
  },
  
  user: ({ id }) => {
    return new Promise((resolve, reject) => {
      const query = `SELECT * FROM users WHERE id = ${id}`;
      db.get(query, async (err, user) => {
        if (err) {
          reject(new Error(`Database error: ${err.message} - Query: ${query}`));
        } else if (user) {
          try {
            const documents = await getUserDocuments(user.id);
            resolve({ ...user, documents });
          } catch (error) {
            reject(error);
          }
        } else {
          resolve(null);
        }
      });
    });
  },
  
  searchUsers: ({ username }) => {
    return new Promise((resolve, reject) => {
      const query = `SELECT * FROM users WHERE username LIKE '%${username}%'`;
      db.all(query, (err, rows) => {
        if (err) {
          reject(new Error(`Search failed: ${err.message} - Query: ${query}`));
        } else {
          resolve(rows);
        }
      });
    });
  },
  
  documents: () => {
    return new Promise((resolve, reject) => {
      // Only return non-confidential documents
      db.all('SELECT * FROM documents WHERE confidential = 0', async (err, docs) => {
        if (err) {
          reject(err);
        } else {
          try {
            const docsWithOwners = await Promise.all(
              docs.map(async (doc) => {
                const owner = await getDocumentOwner(doc.user_id);
                return { ...doc, confidential: !!doc.confidential, owner };
              })
            );
            resolve(docsWithOwners);
          } catch (error) {
            reject(error);
          }
        }
      });
    });
  },
  
  document: ({ id }) => {
    return new Promise((resolve, reject) => {
      // Only return non-confidential documents
      db.get('SELECT * FROM documents WHERE id = ? AND confidential = 0', [id], async (err, doc) => {
        if (err) {
          reject(new Error(`Database error: ${err.message}`));
        } else if (doc) {
          try {
            const owner = await getDocumentOwner(doc.user_id);
            resolve({ ...doc, confidential: !!doc.confidential, owner });
          } catch (error) {
            reject(error);
          }
        } else {
          resolve(null);
        }
      });
    });
  }
};

app.use('/graphql', graphqlHTTP({
  schema: schema,
  rootValue: root,
  graphiql: true,
}));

app.get('/', (req, res) => {
  res.redirect('/graphql');
});

const PORT = process.env.PORT || 5000;

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`GraphQL endpoint: http://localhost:${PORT}/graphql`);
});