import os
import graphene
from flask import Flask, request, jsonify, redirect, Response

# Check FLAG environment variable at startup
if not os.getenv('FLAG'):
    print("ERROR: FLAG environment variable not set!")
    exit(1)

app = Flask(__name__)

class User(graphene.ObjectType):
    id = graphene.Int()
    username = graphene.String()
    email = graphene.String()

class PublicData(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    content = graphene.String()

# Create a Query class that includes the flag in field name
flag = os.getenv('FLAG')
# Create field name with two underscores replacing braces
# This should work well with GraphQL's camelCase conversion
field_name = flag.replace('{', '___').replace('}', '__').replace('-', '__')
print(f"Original flag: {flag}")
print(f"Generated field name: {field_name}")

# Dynamically create Query class with flag in field name
QueryFields = {
    'users': graphene.List(User),
    'public_data': graphene.List(PublicData),
    field_name: graphene.String(),
    'resolve_users': lambda self, info: [
        User(id=1, username="admin", email="admin@company.com"),
        User(id=2, username="user1", email="user1@company.com")
    ],
    'resolve_public_data': lambda self, info: [
        PublicData(id=1, title="Welcome", content="This is public information"),
        PublicData(id=2, title="About", content="Simple GraphQL API")
    ]
}

# Create the Query class dynamically
FinalQuery = type('Query', (graphene.ObjectType,), QueryFields)

schema = graphene.Schema(query=FinalQuery)

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