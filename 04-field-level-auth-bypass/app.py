import os
import graphene
from flask import Flask, request, jsonify, redirect, Response

# Check FLAG environment variable at startup
if not os.getenv('FLAG'):
    print("ERROR: FLAG environment variable not set!")
    exit(1)

app = Flask(__name__)

# Data storage
USERS_DATA = [
    {"id": 1, "username": "john_doe", "email": "john@company.com", "role": "employee"},
    {"id": 2, "username": "jane_smith", "email": "jane@company.com", "role": "manager"},
    {"id": 3, "username": "admin_user", "email": "admin@company.com", "role": "admin"}
]

DOCUMENTS_DATA = [
    {"id": 1, "title": "Public Document", "content": "This is public content", "confidential": False, "internal_ref": "DOC_001", "debug_info": "Public access", "user_id": 1},
    {"id": 2, "title": "Confidential Report", "content": "Secret business data", "confidential": True, "internal_ref": "SECRET_002", "debug_info": os.getenv('FLAG'), "user_id": 3},
    {"id": 3, "title": "User Manual", "content": "How to use the system", "confidential": False, "internal_ref": "DOC_003", "debug_info": "General documentation", "user_id": 2}
]


class User(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()
    role = graphene.String()
    documents = graphene.List(lambda: Document)
    
    def resolve_documents(self, info):
        # Get documents assigned to this user (only non-confidential ones)
        user_docs = [doc for doc in DOCUMENTS_DATA if doc["user_id"] == self.id and not doc["confidential"]]
        return [Document(**doc) for doc in user_docs]

class Document(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    content = graphene.String()
    confidential = graphene.Boolean()
    internal_ref = graphene.String()  # Less obvious field name
    debug_info = graphene.String()    # Another less obvious field name
    user_id = graphene.Int()
    owner = graphene.Field(lambda: User)
    
    def resolve_owner(self, info):
        # Find the user who owns this document
        user_data = next((user for user in USERS_DATA if user["id"] == self.user_id), None)
        return User(**user_data) if user_data else None

class Query(graphene.ObjectType):
    users = graphene.List(User)
    user = graphene.Field(User, id=graphene.Int(required=True))
    documents = graphene.List(Document, user_id=graphene.Int(required=True))
    document = graphene.Field(Document, id=graphene.Int(required=True))
    debug = graphene.Field(Document, user_id=graphene.Int(required=True), id=graphene.Int(required=True))
    
    def resolve_users(self, info):
        return [User(**user) for user in USERS_DATA]
    
    def resolve_user(self, info, id):
        user_data = next((user for user in USERS_DATA if user["id"] == id), None)
        return User(**user_data) if user_data else None
    
    def resolve_documents(self, info, user_id):
        # Get documents for specific user, filter out confidential documents
        user_docs = [doc for doc in DOCUMENTS_DATA if doc["user_id"] == user_id and not doc["confidential"]]
        return [Document(**doc) for doc in user_docs]
    
    def resolve_document(self, info, id):
        # This field requires authorization - should return error without proper auth
        # This demonstrates the vulnerability where authorization is missing on this field
        raise Exception("Unauthorized: Document access requires proper authorization")
    
    def resolve_debug(self, info, user_id, id):
        # Filter to only confidential documents for specific user
        confidential_docs = [doc for doc in DOCUMENTS_DATA if doc["confidential"] and doc["user_id"] == user_id]
        doc_data = next((doc for doc in confidential_docs if doc["id"] == id), None)
        
        if not doc_data:
            raise Exception("No confidential document found for user")
            
        return Document(**doc_data)

schema = graphene.Schema(query=Query)

@app.route('/graphql', methods=['GET', 'POST'])
def graphql_endpoint():
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
        query = data.get('query', '')
        variables = data.get('variables', {})
        
        # Execute the GraphQL query
        result = schema.execute(query, variable_values=variables, context={'request': request})
        
        # Format response
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)