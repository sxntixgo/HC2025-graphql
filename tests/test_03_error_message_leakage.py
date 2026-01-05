#!/usr/bin/env python3
"""
Error Message Leakage Challenge Tests
Tests for GraphQL error message information leakage vulnerability
"""

import requests
import json
import sys
import time
import subprocess
import os
from urllib.parse import urljoin


class TestErrorMessageLeakageChallenge:
    """Test suite for Error Message Leakage Challenge"""
    
    def __init__(self, base_url="http://localhost:8003"):
        self.base_url = base_url
        self.graphql_url = urljoin(base_url, "/graphql")
        self.health_url = urljoin(base_url, "/health")
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Error-Message-Leakage-Test/1.0'
        })
        # Flag will be discovered through error message leakage
        self.tests_passed = 0
        self.tests_failed = 0
    
    def start_services(self):
        """Start Docker Compose services"""
        print("🚀 Starting Error Message Leakage Challenge...")
        try:
            # Change to challenge directory
            os.chdir('../03-error-message-leakage')
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
            os.chdir('../03-error-message-leakage')
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
        subprocess.run(['docker-compose', '-f', 'docker-compose-dev.yml', 'logs'], 
                      capture_output=False)
        return False
    
    def graphql_query(self, query, variables=None):
        """Execute a GraphQL query"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        
        response = self.session.post(self.graphql_url, json=payload)
        return response
    
    def test_flag_leakage(self, description, query, expected_flag):
        """Test if a GraphQL query leaks the flag in error messages"""
        print(f"🧪 Test: {description}")
        
        try:
            response = self.graphql_query(query)
            response_text = response.text
            
            if expected_flag in response_text:
                print("✅ PASS - Flag leaked in error message")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Flag not found in error message")
                print(f"Response: {response_text}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def test_valid_access(self, description, query, expected_content):
        """Test valid access that should not leak flags"""
        print(f"🧪 Test: {description}")
        
        try:
            response = self.graphql_query(query)
            response_text = response.text
            
            if expected_content in response_text and "HC{" not in response_text:
                print("✅ PASS - Valid access works without flag leakage")
                self.tests_passed += 1
                return True
            else:
                print("❌ FAIL - Valid access failed or flag leaked inappropriately")
                print(f"Response: {response_text}")
                self.tests_failed += 1
                return False
        except Exception as e:
            print(f"❌ FAIL - Exception occurred: {e}")
            self.tests_failed += 1
            return False
    
    def run_tests(self):
        """Run all error message leakage tests"""
        print("🔍 Error Message Leakage Challenge Test Runner")
        print("==============================================")
        
        if not self.start_services():
            return False
        
        try:
            if not self.wait_for_service():
                return False
            
            print("\n🧪 Running error message leakage tests...\n")
            
            # Test 1: Invalid user ID type (should leak flag in type validation error)
            self.test_flag_leakage(
                "Invalid user ID type validation",
                'query { userById(id: "invalid_string") { id username } }',
                "HC{"
            )
            
            # Test 2: Search query too long (should leak flag in length validation error)
            self.test_flag_leakage(
                "Search query length validation",
                'query { searchUsers(query: "this_is_a_very_long_search_query_that_exceeds_fifty_characters_limit") { id username } }',
                "HC{"
            )
            
            # Test 3: File path traversal attempt (should leak flag in security error)
            self.test_flag_leakage(
                "File path traversal validation",
                'query { fileByName(filename: "../../../etc/passwd") { id filename content } }',
                "HC{"
            )
            
            # Test 4: Invalid file extension (should leak flag in file type error)
            self.test_flag_leakage(
                "File extension validation",
                'query { fileByName(filename: "malicious.exe") { id filename content } }',
                "HC{"
            )
            
            # Test 5: Non-existent file (should leak flag in file not found error)
            self.test_flag_leakage(
                "File not found error",
                'query { fileByName(filename: "nonexistent.txt") { id filename content } }',
                "HC{"
            )
            
            # Test 6: Trigger database connection timeout error with large user ID
            self.test_flag_leakage(
                "Database connection timeout error",
                'query { userById(id: "9999") { id username email } }',
                "HC{"
            )
            
            print("\n🧪 Testing legitimate access (should not leak flag)...\n")
            
            # Test 7: Valid file access (should work without errors)
            self.test_valid_access(
                "Valid file access",
                'query { fileByName(filename: "config.txt") { id filename content } }',
                "Database connection: localhost:5432"
            )
            
            # Test 8: Valid user access (should work without errors)
            self.test_valid_access(
                "Valid user access",
                'query { userById(id: "1") { id username email } }',
                "admin"
            )
            
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
    tester = TestErrorMessageLeakageChallenge()
    success = tester.run_tests()
    
    if success:
        print("\n🎉 Error Message Leakage Challenge tests completed successfully!")
        print("All tests demonstrate that the flag is properly leaked in various error messages.")
        sys.exit(0)
    else:
        print("\n❌ Error Message Leakage Challenge tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()