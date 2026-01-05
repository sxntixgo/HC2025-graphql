#!/usr/bin/env python3
"""
Schema Introspection Challenge Tests
Tests for GraphQL schema introspection vulnerability
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestSchemaIntrospectionChallenge:
    """Test suite for Schema Introspection Challenge"""
    
    def __init__(self, base_url="http://localhost:8002"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.health_url = urljoin(base_url, "/health")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Schema-Introspection-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting Schema Introspection Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../02-schema-introspection')
            subprocess.run(['docker-compose', '-f', 'docker-compose-dev.yml', 'up', '-d'], 
                         check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e}")
            return False
        finally:
            # Change back to tests directory
            os.chdir('../tests')
    
    def stop_services(self):
        """Stop Docker Compose services"""
        print("🧹 Cleaning up...")
        try:
            # Change to challenge directory
            os.chdir('../02-schema-introspection')
            subprocess.run(['docker-compose', '-f', 'docker-compose-dev.yml', 'down'], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to stop services: {e}")
        finally:
            # Change back to tests directory
            os.chdir('../tests')
    
    def wait_for_service(self, timeout=120):
        """Wait for the service to be ready"""
        print("⏳ Waiting for services to be ready...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(self.health_url)
                if response.status_code == 200:
                    print("✅ Services are ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        
        print(f"❌ Services failed to start within {timeout}s")
        return False
    
    def graphql_query(self, query, variables=None):
        """Execute a GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self.session.post(self.graphql_url, json=payload)
        return response
    
    def test_service_accessibility(self):
        """Test that the service is accessible"""
        print("🧪 Test: Service accessibility")
        
        try:
            # Test GraphQL endpoint accessibility
            response = self.session.get(self.graphql_url)
            if response.status_code in [200, 302]:  # 200 for GraphiQL, 302 for redirect
                print("✅ PASS - GraphQL endpoint accessible")
                self.tests_passed += 1
                return True
            else:
                print(f"❌ FAIL - GraphQL endpoint returned status {response.status_code}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_basic_graphql_functionality(self):
        """Test basic GraphQL functionality"""
        print("🧪 Test: Basic GraphQL functionality")
        
        try:
            query = """
            query {
                users {
                    id
                    username
                    email
                }
            }
            """
            
            response = self.graphql_query(query)
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data and "users" in data["data"]:
                    print("✅ PASS - Basic GraphQL queries work")
                    self.tests_passed += 1
                    return True
            
            print("❌ FAIL - Basic GraphQL query failed")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_schema_introspection_reveals_hidden_field(self):
        """Test that schema introspection reveals hidden admin fields"""
        print("🧪 Test: Schema introspection reveals hidden admin fields")
        
        try:
            # Perform deep introspection to find admin_notes field
            introspection_query = """
            query IntrospectionQuery {
              __schema {
                queryType {
                  fields {
                    name
                    description
                    type {
                      name
                      kind
                      fields {
                        name
                        description
                      }
                    }
                  }
                }
              }
            }
            """
            
            response = self.graphql_query(introspection_query)
            
            if response.status_code != 200:
                print(f"❌ FAIL - Introspection query failed with status {response.status_code}")
                self.tests_failed += 1
                return False
            
            response_data = response.json()
            
            # Look for admin_notes field in the schema
            found_admin_field = False
            if 'data' in response_data and '__schema' in response_data['data']:
                fields = response_data['data']['__schema']['queryType']['fields']
                field_names = [field['name'] for field in fields]
                
                if 'adminNotes' in field_names or 'admin_notes' in field_names:
                    found_admin_field = True
                    print("✅ PASS - Hidden admin field discovered through introspection")
                    
                    # Try to access the admin field to get the flag
                    admin_query = "{ adminNotes { id title content flag } }"
                    admin_response = self.graphql_query(admin_query)
                    
                    if admin_response.status_code == 200:
                        admin_data = admin_response.json()
                        if 'data' in admin_data and 'adminNotes' in admin_data['data']:
                            print("✅ PASS - Successfully accessed hidden admin data with flag")
                            self.tests_passed += 1
                            return True
            
            if not found_admin_field:
                print("❌ FAIL - No hidden admin field found in schema introspection")
                print(f"Available fields: {field_names}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all schema introspection tests"""
        print("🔍 Schema Introspection Challenge Test Runner")
        print("============================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running schema introspection tests...\n")
            
            # Run tests
            self.test_service_accessibility()
            self.test_basic_graphql_functionality()
            self.test_schema_introspection_reveals_hidden_field()
            
            print(f"\n📊 Test Results: {self.tests_passed} passed, {self.tests_failed} failed")
            
            if self.tests_failed > 0:
                print("❌ Some tests failed")
                return False
            else:
                print("✅ All tests passed!")
                return True
                
        finally:
            self.stop_services()


def main():
    """Main function"""
    tester = TestSchemaIntrospectionChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Schema Introspection Challenge tests completed successfully!")
        print("Hidden admin fields were discoverable through GraphQL introspection!")
        sys.exit(0)
    else:
        print("\n❌ Schema Introspection Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()