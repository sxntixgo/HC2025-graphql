const express = require('express');
const { graphqlHTTP } = require('express-graphql');
const { buildSchema, GraphQLScalarType, GraphQLError } = require('graphql');
const { MongoClient } = require('mongodb');

const app = express();

let db;
const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = 'ctf_challenge';

async function initializeDB() {
  try {
    const client = new MongoClient(MONGO_URL);
    await client.connect();
    db = client.db(DB_NAME);
    console.log('Connected to MongoDB');
    
    await seedData();
  } catch (error) {
    console.error('MongoDB connection error:', error);
    // Fallback to in-memory storage for demo
    initInMemoryDB();
  }
}

async function seedData() {
  try {
    // Clear existing data
    await db.collection('users').deleteMany({});
    await db.collection('documents').deleteMany({});

    if (!process.env.FLAG) {
      console.error('ERROR: FLAG environment variable is required but not set');
      process.exit(1);
    }

    const users = [
      {
        _id: 1,
        username: 'john_doe',
        email: 'john@company.com',
        role: 'employee'
      },
      {
        _id: 2,
        username: 'jane_smith',
        email: 'jane@company.com',
        role: 'manager'
      },
      {
        _id: 3,
        username: 'admin_user',
        email: 'admin@company.com',
        role: 'admin'
      }
    ];

    const documents = [
      {
        _id: 1,
        title: 'Public Document',
        content: 'This is public content',
        confidential: false,
        internal_ref: 'DOC_001',
        debug_info: 'Public access allowed',
        user_id: 1
      },
      {
        _id: 2,
        title: '--',
        content: 'Secret business data',
        confidential: true,
        internal_ref: 'SECRET_002',
        debug_info: process.env.FLAG,
        user_id: 3
      },
      {
        _id: 3,
        title: 'User Manual',
        content: 'How to use the system',
        confidential: false,
        internal_ref: 'DOC_003',
        debug_info: 'General documentation',
        user_id: 2
      },
      {
        _id: 4,
        title: 'Internal Memo',
        content: 'Company internal communication',
        confidential: true,
        internal_ref: 'MEMO_004',
        debug_info: 'Internal use only',
        user_id: 2
      }
    ];

    await db.collection('users').insertMany(users);
    await db.collection('documents').insertMany(documents);

    console.log('Database seeded successfully');
  } catch (error) {
    console.error('Error seeding database:', error);
  }
}

// In-memory fallback
let inMemoryDB = {};

function initInMemoryDB() {
  console.log('Using in-memory database fallback');
  
  if (!process.env.FLAG) {
    console.error('ERROR: FLAG environment variable is required but not set');
    process.exit(1);
  }
  
  inMemoryDB = {
    users: [
      { _id: 1, username: 'john_doe', email: 'john@company.com', role: 'employee' },
      { _id: 2, username: 'jane_smith', email: 'jane@company.com', role: 'manager' },
      { _id: 3, username: 'admin_user', email: 'admin@company.com', role: 'admin' }
    ],
    documents: [
      { _id: 1, title: 'Public Document', content: 'This is public content', confidential: false, internal_ref: 'DOC_001', debug_info: 'Public access allowed', user_id: 1 },
      { _id: 2, title: '--', content: 'Secret business data', confidential: true, internal_ref: 'SECRET_002', debug_info: process.env.FLAG, user_id: 3 },
      { _id: 3, title: 'User Manual', content: 'How to use the system', confidential: false, internal_ref: 'DOC_003', debug_info: 'General documentation', user_id: 2 },
      { _id: 4, title: 'Internal Memo', content: 'Company internal communication', confidential: true, internal_ref: 'MEMO_004', debug_info: 'Internal use only', user_id: 2 }
    ]
  };
}

const schema = buildSchema(`
  type User {
    _id: Int
    username: String
    email: String
    role: String
    documents: [Document]
  }

  type Document {
    _id: Int
    title: String
    content: String
    confidential: Boolean
    internal_ref: String
    debug_info: String
    user_id: Int
    owner: User
  }

  scalar JSON

  type Query {
    users: [User]
    user(_id: Int!): User
    documents: [Document]
    document(_id: Int!): Document
    searchUsers(username: String!): [User]
    searchDocuments(titleFilter: JSON!): [Document]
  }
`);

// Helper functions
const getUserDocuments = async (userId) => {
  try {
    if (db) {
      const docs = await db.collection('documents').find({ user_id: userId, confidential: false }).toArray();
      return await Promise.all(docs.map(async (doc) => {
        const owner = await getDocumentOwner(doc.user_id);
        return { ...doc, owner };
      }));
    }
    const docs = inMemoryDB.documents.filter(d => d.user_id === userId && !d.confidential);
    return docs.map(doc => {
      const owner = inMemoryDB.users.find(u => u._id === doc.user_id);
      return { ...doc, owner };
    });
  } catch (error) {
    throw new Error(`User documents fetch failed: ${error.message}`);
  }
};

const getDocumentOwner = async (userId) => {
  try {
    if (db) {
      return await db.collection('users').findOne({ _id: userId });
    }
    return inMemoryDB.users.find(u => u._id === userId);
  } catch (error) {
    throw new Error(`Document owner fetch failed: ${error.message}`);
  }
};

// JSON scalar type implementation
const JSONType = new GraphQLScalarType({
  name: 'JSON',
  serialize: (value) => value,
  parseValue: (value) => value,
  parseLiteral: (ast) => {
    throw new GraphQLError('JSON scalar cannot be used in query literals. Use variables instead.');
  }
});

const root = {
  JSON: JSONType,
  
  users: async () => {
    try {
      if (db) {
        const users = await db.collection('users').find({}).toArray();
        return await Promise.all(users.map(async (user) => {
          const documents = await getUserDocuments(user._id);
          return { ...user, documents };
        }));
      }
      return await Promise.all(inMemoryDB.users.map(async (user) => {
        const documents = await getUserDocuments(user._id);
        return { ...user, documents };
      }));
    } catch (error) {
      throw new Error(`Users fetch failed: ${error.message}`);
    }
  },

  user: async ({ _id }) => {
    try {
      if (db) {
        const user = await db.collection('users').findOne({ _id: _id });
        if (user) {
          const documents = await getUserDocuments(user._id);
          return { ...user, documents };
        }
        return null;
      }
      const user = inMemoryDB.users.find(u => u._id === _id);
      if (user) {
        const documents = await getUserDocuments(user._id);
        return { ...user, documents };
      }
      return null;
    } catch (error) {
      throw new Error(`User lookup failed: ${error.message} - Query: ${JSON.stringify({ _id })}`);
    }
  },

  documents: async () => {
    try {
      if (db) {
        const docs = await db.collection('documents').find({ confidential: false }).toArray();
        return await Promise.all(docs.map(async (doc) => {
          const owner = await getDocumentOwner(doc.user_id);
          return { ...doc, owner };
        }));
      }
      const docs = inMemoryDB.documents.filter(d => !d.confidential);
      return docs.map(doc => {
        const owner = inMemoryDB.users.find(u => u._id === doc.user_id);
        return { ...doc, owner };
      });
    } catch (error) {
      throw new Error(`Documents fetch failed: ${error.message}`);
    }
  },

  document: async ({ _id }) => {
    try {
      if (db) {
        const doc = await db.collection('documents').findOne({ _id: _id, confidential: false });
        if (doc) {
          const owner = await getDocumentOwner(doc.user_id);
          return { ...doc, owner };
        }
        return null;
      }
      const doc = inMemoryDB.documents.find(d => d._id === _id && !d.confidential);
      if (doc) {
        const owner = inMemoryDB.users.find(u => u._id === doc.user_id);
        return { ...doc, owner };
      }
      return null;
    } catch (error) {
      throw new Error(`Document lookup failed: ${error.message} - Query: ${JSON.stringify({ _id })}`);
    }
  },

  searchUsers: async ({ username }) => {
    try {
      if (db) {
        // Vulnerable: Direct regex injection in MongoDB
        const query = { username: { $regex: username } };
        const users = await db.collection('users').find(query).toArray();
        return await Promise.all(users.map(async (user) => {
          const documents = await getUserDocuments(user._id);
          return { ...user, documents };
        }));
      }
      const users = inMemoryDB.users.filter(u => u.username.includes(username));
      return await Promise.all(users.map(async (user) => {
        const documents = await getUserDocuments(user._id);
        return { ...user, documents };
      }));
    } catch (error) {
      throw new Error(`User search failed: ${error.message} - Query: ${JSON.stringify({ username: { $regex: username } })}`);
    }
  },

  searchDocuments: async ({ titleFilter }) => {
    try {
      if (db) {
        // Check for regex filters and validate them
        if (titleFilter && typeof titleFilter === 'object') {
          if (titleFilter.$regex !== undefined || titleFilter.$regexp !== undefined) {
            const regexValue = titleFilter.$regex || titleFilter.$regexp;
            // Only allow non-empty alphanumeric characters in regex patterns for security
            if (!regexValue || typeof regexValue !== 'string' || regexValue.trim() === '' || !/^[a-zA-Z0-9]+$/.test(regexValue)) {
              throw new Error('Regex patterns must be non-empty and can only contain alphanumeric characters (a-zA-Z0-9)');
            }
          }
        }
        
        // Vulnerable: Direct NoSQL injection - titleFilter object is used directly in MongoDB query
        const query = { title: titleFilter };
        
        const docs = await db.collection('documents').find(query).toArray();
        return await Promise.all(docs.map(async (doc) => {
          const owner = await getDocumentOwner(doc.user_id);
          return { ...doc, owner };
        }));
      }
      // For in-memory fallback, simulate some basic filtering
      if (titleFilter && typeof titleFilter === 'object') {
        // Check for regex filters and validate them
        if (titleFilter.$regex !== undefined || titleFilter.$regexp !== undefined) {
          const regexValue = titleFilter.$regex || titleFilter.$regexp;
          // Only allow non-empty alphanumeric characters in regex patterns for security
          if (!regexValue || typeof regexValue !== 'string' || regexValue.trim() === '' || !/^[a-zA-Z0-9]+$/.test(regexValue)) {
            throw new Error('Regex patterns must be non-empty and can only contain alphanumeric characters (a-zA-Z0-9)');
          }
        }
        
        if (titleFilter.$ne !== undefined) {
          const docs = inMemoryDB.documents.filter(d => d.title !== titleFilter.$ne);
          return docs.map(doc => {
            const owner = inMemoryDB.users.find(u => u._id === doc.user_id);
            return { ...doc, owner };
          });
        }
        if (titleFilter.$regex !== undefined) {
          const docs = inMemoryDB.documents.filter(d => new RegExp(titleFilter.$regex).test(d.title));
          return docs.map(doc => {
            const owner = inMemoryDB.users.find(u => u._id === doc.user_id);
            return { ...doc, owner };
          });
        }
        if (titleFilter.$exists !== undefined && titleFilter.$exists) {
          const docs = inMemoryDB.documents.filter(d => d.title !== undefined);
          return docs.map(doc => {
            const owner = inMemoryDB.users.find(u => u._id === doc.user_id);
            return { ...doc, owner };
          });
        }
      }
      return [];
    } catch (error) {
      throw new Error(`Document search failed: ${error.message} - Query: ${JSON.stringify({ title: titleFilter })}`);
    }
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

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

const PORT = process.env.PORT || 5000;

initializeDB().then(() => {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`GraphQL endpoint: http://localhost:${PORT}/graphql`);
  });
});