import os
import graphene
from flask import Flask, request, jsonify, redirect, Response

# Check FLAG environment variable at startup
if not os.getenv('FLAG'):
    print("ERROR: FLAG environment variable not set!")
    exit(1)

app = Flask(__name__)

# Simple in-memory data - no database needed
USERS_DATA = [
    {"id": 1, "username": "admin", "email": "admin@company.com"},
    {"id": 2, "username": "john", "email": "john@company.com"},
    {"id": 3, "username": "jane", "email": "jane@company.com"}
]

FILES_DATA = [
    {"id": 1, "filename": "config.txt", "content": "Database connection: localhost:5432"},
    {"id": 2, "filename": "secrets.txt", "content": "API Keys and passwords"},
    {"id": 3, "filename": "backup.sql", "content": "Database backup file"}
]

class User(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()

class File(graphene.ObjectType):
    id = graphene.Int()
    filename = graphene.String()
    content = graphene.String()

class Query(graphene.ObjectType):
    users = graphene.List(User)
    user_by_id = graphene.Field(User, id=graphene.String(required=True))
    search_users = graphene.Field(graphene.List(User), query=graphene.String(required=True))
    file_by_name = graphene.Field(File, filename=graphene.String(required=True))
    
    def resolve_users(self, info):
        return [User(**user) for user in USERS_DATA]
    
    def resolve_user_by_id(self, info, id):
        try:
            # Intentional type validation error that leaks flag
            user_id = int(id)
            # Simulate database connection error for large user IDs
            if user_id > 1000:
                flag = os.getenv('FLAG')
                raise Exception(f"Database connection timeout: User ID {user_id} out of range [INTERNAL: FLAG={flag}, MAX_USER_ID=1000, DB_STATUS=timeout]")
            user = next((u for u in USERS_DATA if u["id"] == user_id), None)
            if user:
                return User(**user)
            return None
        except ValueError as e:
            # Leak flag in type validation errors
            flag = os.getenv('FLAG')
            raise Exception(f"Type validation failed: {str(e)} [DEBUG: FLAG={flag}, INPUT_TYPE=string, EXPECTED_TYPE=integer, USER_TABLE=users]")
        except Exception as e:
            # Leak flag in general errors
            flag = os.getenv('FLAG')
            raise Exception(f"User lookup failed: {str(e)} [INTERNAL: FLAG={flag}, USERS_COUNT={len(USERS_DATA)}]")
    
    def resolve_search_users(self, info, query):
        try:
            # Input validation that leaks flag in length errors
            if len(query) > 50:
                flag = os.getenv('FLAG')
                raise Exception(f"Search query too long: {len(query)} characters [LIMIT: 50, FLAG={flag}, MAX_SEARCH_LENGTH=50]")
            
            # Simple search simulation
            results = [u for u in USERS_DATA if query.lower() in u["username"].lower()]
            return [User(**user) for user in results]
            
        except Exception as e:
            # Leak flag in search validation errors
            flag = os.getenv('FLAG')
            raise Exception(f"Search validation error: {str(e)} [SEARCH_ENGINE_FLAG={flag}]")
    
    def resolve_file_by_name(self, info, filename):
        try:
            # Security validation that leaks flag
            if "../" in filename or ".." in filename:
                flag = os.getenv('FLAG')
                raise Exception(f"Path traversal detected: {filename} [SECURITY_FLAG={flag}, BLOCKED_PATTERNS=../, ..]")
            
            # File extension validation that leaks flag
            if filename.endswith(('.exe', '.bat', '.sh')):
                flag = os.getenv('FLAG')
                raise Exception(f"Dangerous file type: {filename} [CONFIG_FLAG={flag}, ALLOWED_EXTENSIONS=txt,sql,json]")
            
            # File lookup
            file_obj = next((f for f in FILES_DATA if f["filename"] == filename), None)
            if file_obj:
                return File(**file_obj)
            
            # File not found error that leaks flag
            flag = os.getenv('FLAG')
            raise Exception(f"File not found: {filename} [SYSTEM_FLAG={flag}, AVAILABLE_FILES={[f['filename'] for f in FILES_DATA]}]")
            
        except Exception as e:
            # Leak flag in file system errors
            flag = os.getenv('FLAG')
            raise Exception(f"File system error: {str(e)} [INTERNAL: FLAG={flag}, FILE_SYSTEM=virtual, ACCESS_MODE=read]")

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
        result = schema.execute(query, variable_values=variables)
        
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