#!/usr/bin/env python3
"""
Naive Introspection Challenge Tests
Tests for GraphQL naive introspection vulnerability where flag is exposed in field names
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestNaiveIntrospectionChallenge:
    """Test suite for Naive Introspection Challenge"""
    
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.root_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Naive-Introspection-Test/1.0'
        })
        # Flag will be discovered through introspection
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting Naive Introspection Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../01-naive-introspection')
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
            os.chdir('../01-naive-introspection')
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
    
    def graphql_query(self, query, variables=None):
        """Execute a GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self.session.post(self.graphql_url, json=payload)
        return response
    
    def test_basic_introspection_reveals_flag(self):
        """Test that basic introspection reveals the flag in field names"""
        print("🧪 Test: Basic introspection reveals flag in field names")
        
        try:
            # Perform introspection query to get field names
            introspection_query = """
            query IntrospectionQuery {
              __schema {
                queryType {
                  fields {
                    name
                    type {
                      name
                      ofType {
                        name
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
            
            # Check if introspection data is present
            if 'data' not in response_data or '__schema' not in response_data['data']:
                print("❌ FAIL - Invalid introspection response structure")
                self.tests_failed += 1
                return False
            
            # Extract field names
            fields = response_data['data']['__schema']['queryType']['fields']
            field_names = [field['name'] for field in fields]
            
            # Look for a field name that contains flag-like information
            flag_field = None
            for field_name in field_names:
                if ('HC' in field_name and 'flag' in field_name.lower()) or 'HC__' in field_name:
                    flag_field = field_name
                    break
            
            if flag_field:
                print(f"✅ PASS - Flag found in field name: {flag_field}")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - No field containing flag information found")
                print(f"Available fields: {field_names}")
                self.tests_failed += 1
                return False
                
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_service_accessibility(self):
        """Test that the service is accessible"""
        print("🧪 Test: Service accessibility")
        
        try:
            # Test GraphQL endpoint accessibility
            response = self.session.get(self.graphql_url)
            if response.status_code == 200:
                print("✅ PASS - GraphQL endpoint accessible")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - GraphQL endpoint not accessible")
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
            # Test basic query
            query = """
            query {
              users {
                id
                username
              }
            }
            """
            
            response = self.graphql_query(query)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'data' in response_data and 'users' in response_data['data']:
                    print("✅ PASS - Basic GraphQL queries work")
                    self.tests_passed += 1
                    return True
            
            print("❌ FAIL - Basic GraphQL query failed")
            self.tests_failed += 1
            return False
            
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all naive introspection tests"""
        print("🔍 Naive Introspection Challenge Test Runner")
        print("============================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running naive introspection tests...\n")
            
            # Run tests
            self.test_service_accessibility()
            self.test_basic_graphql_functionality() 
            self.test_basic_introspection_reveals_flag()
            
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
    tester = TestNaiveIntrospectionChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Naive Introspection Challenge tests completed successfully!")
        print("The flag is exposed in the GraphQL field names during introspection!")
        sys.exit(0)
    else:
        print("\n❌ Naive Introspection Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()