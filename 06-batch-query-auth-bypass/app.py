import os
import graphene
import time
from flask import Flask, request, jsonify, redirect
from functools import wraps

# Check FLAG environment variable at startup
if not os.getenv('FLAG'):
    print("ERROR: FLAG environment variable not set!")
    exit(1)

app = Flask(__name__)

# Global flag to track if we're in a batch query context
is_batch_query = False

def rate_limit(max_requests=5):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            global is_batch_query
            resolver_name = f.__name__
            
            # Special handling for adminDocuments - rate limit = 0 means blocked
            if resolver_name == 'resolve_admin_documents' and max_requests == 0:
                if not is_batch_query:
                    raise Exception("Rate limit reached for adminDocuments endpoint.")
            
            # Special handling for sensitiveUser - rate limit = 0 means blocked
            if resolver_name == 'resolve_sensitive_user' and max_requests == 0:
                if not is_batch_query:
                    raise Exception("Rate limit reached for sensitiveUser endpoint.")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Data storage (same structure as 04-graphql-injection)
USERS_DATA = [
    {"id": 1, "username": "john_doe", "email": "john@company.com", "role": "employee"},
    {"id": 2, "username": "jane_smith", "email": "jane@company.com", "role": "manager"},
    {"id": 3, "username": "admin_user", "email": "admin@company.com", "role": "admin"}
]

DOCUMENTS_DATA = [
    {"id": 1, "title": "Public Document", "content": "This is public content", "confidential": False, "internal_ref": "DOC_001", "debug_info": "Public access allowed", "user_id": 1},
    {"id": 2, "title": "Confidential Report", "content": "Secret business data", "confidential": True, "internal_ref": "SECRET_002", "debug_info": os.getenv('FLAG'), "user_id": 3},
    {"id": 3, "title": "User Manual", "content": "How to use the system", "confidential": False, "internal_ref": "DOC_003", "debug_info": "General documentation", "user_id": 2},
    {"id": 4, "title": "Internal Memo", "content": "Company internal communication", "confidential": True, "internal_ref": "MEMO_004", "debug_info": "Internal use only", "user_id": 2}
]

class User(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    role = graphene.String()
    documents = graphene.List(lambda: Document)

class Document(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    content = graphene.String()
    confidential = graphene.Boolean()
    internal_ref = graphene.String()
    debug_info = graphene.String()
    owner = graphene.Field(User)

def get_user_documents(user_id):
    """Get non-confidential documents for a user"""
    return [doc for doc in DOCUMENTS_DATA if doc['user_id'] == user_id and not doc['confidential']]

def get_document_owner(user_id):
    """Get the owner of a document"""
    return next((user for user in USERS_DATA if user['id'] == user_id), None)

class Query(graphene.ObjectType):
    users = graphene.List(User)
    user = graphene.Field(User, id=graphene.Int(required=True))
    documents = graphene.List(Document)
    document = graphene.Field(Document, id=graphene.Int(required=True))
    
    # Protected queries with rate limiting
    admin_documents = graphene.List(Document)
    sensitive_user = graphene.Field(User, id=graphene.Int(required=True))
    
    def resolve_users(self, info):
        """Get all users with their non-confidential documents"""
        result = []
        for user_data in USERS_DATA:
            user_docs = get_user_documents(user_data['id'])
            documents = []
            for doc_data in user_docs:
                owner = get_document_owner(doc_data['user_id'])
                # Remove user_id from doc_data since it's not a GraphQL field
                doc_fields = {k: v for k, v in doc_data.items() if k != 'user_id'}
                documents.append(Document(**doc_fields, owner=User(**owner) if owner else None))
            
            result.append(User(**user_data, documents=documents))
        return result
    
    @rate_limit(max_requests=3)
    def resolve_user(self, info, id):
        """Get a specific user with their non-confidential documents"""
        time.sleep(0.1)  # Simulate processing time
        user_data = next((user for user in USERS_DATA if user['id'] == id), None)
        if not user_data:
            return None
            
        user_docs = get_user_documents(user_data['id'])
        documents = []
        for doc_data in user_docs:
            owner = get_document_owner(doc_data['user_id'])
            # Remove user_id from doc_data since it's not a GraphQL field
            doc_fields = {k: v for k, v in doc_data.items() if k != 'user_id'}
            documents.append(Document(**doc_fields, owner=User(**owner) if owner else None))
        
        return User(**user_data, documents=documents)
    
    def resolve_documents(self, info):
        """Get all non-confidential documents"""
        result = []
        for doc_data in DOCUMENTS_DATA:
            if not doc_data['confidential']:
                owner = get_document_owner(doc_data['user_id'])
                # Remove user_id from doc_data since it's not a GraphQL field
                doc_fields = {k: v for k, v in doc_data.items() if k != 'user_id'}
                result.append(Document(**doc_fields, owner=User(**owner) if owner else None))
        return result
    
    @rate_limit(max_requests=2)
    def resolve_document(self, info, id):
        """Get a specific non-confidential document"""
        time.sleep(0.1)  # Simulate processing time
        doc_data = next((doc for doc in DOCUMENTS_DATA if doc['id'] == id and not doc['confidential']), None)
        if not doc_data:
            return None
            
        owner = get_document_owner(doc_data['user_id'])
        # Remove user_id from doc_data since it's not a GraphQL field
        doc_fields = {k: v for k, v in doc_data.items() if k != 'user_id'}
        return Document(**doc_fields, owner=User(**owner) if owner else None)
    
    @rate_limit(max_requests=0)
    def resolve_admin_documents(self, info):
        """Get ALL documents including confidential ones - BLOCKED for individual queries, accessible via batch queries only"""
        time.sleep(0.2)  # Simulate processing time
        result = []
        for doc_data in DOCUMENTS_DATA:
            owner = get_document_owner(doc_data['user_id'])
            # Remove user_id from doc_data since it's not a GraphQL field
            doc_fields = {k: v for k, v in doc_data.items() if k != 'user_id'}
            result.append(Document(**doc_fields, owner=User(**owner) if owner else None))
        return result
    
    @rate_limit(max_requests=0)
    def resolve_sensitive_user(self, info, id):
        """Get user with ALL their documents including confidential ones"""
        time.sleep(0.2)  # Simulate processing time
        user_data = next((user for user in USERS_DATA if user['id'] == id), None)
        if not user_data:
            return None
            
        # Get ALL documents for this user (including confidential)
        user_docs = [doc for doc in DOCUMENTS_DATA if doc['user_id'] == user_data['id']]
        documents = []
        for doc_data in user_docs:
            owner = get_document_owner(doc_data['user_id'])
            # Remove user_id from doc_data since it's not a GraphQL field
            doc_fields = {k: v for k, v in doc_data.items() if k != 'user_id'}
            documents.append(Document(**doc_fields, owner=User(**owner) if owner else None))
        
        return User(**user_data, documents=documents)

schema = graphene.Schema(query=Query)

@app.route('/graphql', methods=['GET', 'POST'])
def graphql_endpoint():
    global is_batch_query
    
    if request.method == 'GET':
        # Return GraphiQL interface for GET requests
        return '''
<!DOCTYPE html>
<html>
<head>
  <title>GraphiQL</title>
  <style>
    body {
      height: 100%;
      margin: 0;
      width: 100%;
      overflow: hidden;
    }
    #graphiql {
      height: 100vh;
    }
  </style>
  <script
    crossorigin
    src="https://unpkg.com/react@17/umd/react.production.min.js"
  ></script>
  <script
    crossorigin
    src="https://unpkg.com/react-dom@17/umd/react-dom.production.min.js"
  ></script>
  <link rel="stylesheet" href="https://unpkg.com/graphiql@1.11.5/graphiql.min.css" />
</head>
<body>
  <div id="graphiql">Loading...</div>
  <script
    src="https://unpkg.com/graphiql@1.11.5/graphiql.min.js"
    type="application/javascript"
  ></script>
  <script>
    const fetcher = GraphiQL.createFetcher({
      url: '/graphql',
    });
    
    ReactDOM.render(
      React.createElement(GraphiQL, {
        fetcher,
        defaultVariableEditorOpen: false,
      }),
      document.getElementById('graphiql'),
    );
  </script>
</body>
</html>
        '''
    
    # Handle POST requests with GraphQL queries
    try:
        data = request.get_json()
        
        # Handle both single queries and batch queries
        if isinstance(data, list):
            # Batch query validation - require minimum 2 queries
            if len(data) < 2:
                return jsonify({
                    'errors': [{'message': 'Batch queries must contain at least 2 queries'}]
                }), 400
            
            # Batch query - set the flag to allow adminDocuments access
            is_batch_query = True
            results = []
            for query_data in data:
                query = query_data.get('query', '')
                variables = query_data.get('variables', {})
                result = schema.execute(query, variable_values=variables, context={'request': request})
                
                response_data = {'data': result.data}
                if result.errors:
                    response_data['errors'] = [{'message': str(error)} for error in result.errors]
                results.append(response_data)
            is_batch_query = False  # Reset after processing
            return jsonify(results)
        else:
            # Single query - adminDocuments will be blocked
            is_batch_query = False
            query = data.get('query', '')
            variables = data.get('variables', {})
            result = schema.execute(query, variable_values=variables, context={'request': request})
            
            response_data = {'data': result.data}
            if result.errors:
                response_data['errors'] = [{'message': str(error)} for error in result.errors]
            return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'errors': [{'message': str(e)}]
        }), 400

@app.route('/')
def index():
    return redirect('/graphql')

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

@app.route('/reset')
def reset():
    # No rate limit state to reset - adminDocuments access is purely batch-query based
    return "No persistent state to reset - adminDocuments access depends on batch queries!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)