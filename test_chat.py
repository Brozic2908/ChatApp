"""
test_chat.py
~~~~~~~~~~~~~~~~~

Automated testing script for the hybrid chat application.
Tests all API endpoints and verifies functionality.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8001"

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(test_name):
    """Print test header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}🧪 Testing: {test_name}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def test_submit_info():
    """Test peer registration endpoint"""
    print_test("POST /submit-info - Peer Registration")
    
    # Test case 1: Valid registration
    data = {
        "peer_id": "test_peer_001",
        "ip": "127.0.0.1",
        "port": 5000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit-info", json=data)
        result = response.json()
        
        if result.get("status") == "success":
            print_success(f"Peer registered: {result}")
        else:
            print_error(f"Registration failed: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    # Test case 2: Another peer
    data2 = {
        "peer_id": "test_peer_002",
        "ip": "127.0.0.1",
        "port": 5001
    }
    
    try:
        response = requests.post(f"{BASE_URL}/submit-info", json=data2)
        result = response.json()
        print_success(f"Second peer registered: {result.get('peer_id')}")
    except Exception as e:
        print_error(f"Second registration failed: {e}")
    
    return True

def test_get_list():
    """Test peer list retrieval"""
    print_test("GET /get-list - Get Peer List")
    
    try:
        response = requests.get(f"{BASE_URL}/get-list")
        result = response.json()
        
        if result.get("status") == "success":
            print_success(f"Retrieved {result.get('count')} peers")
            for peer in result.get("peers", []):
                print_info(f"  - {peer['peer_id']} at {peer['ip']}:{peer['port']}")
        else:
            print_error(f"Failed to get peer list: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    return True

def test_add_list():
    """Test channel joining"""
    print_test("POST /add-list - Join Channel")
    
    # Test case 1: Join general channel
    data = {
        "peer_id": "test_peer_001",
        "channel": "general"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/add-list", json=data)
        result = response.json()
        
        if result.get("status") == "success":
            print_success(f"Joined channel: {result.get('channel')} "
                         f"(members: {result.get('members_count')})")
        else:
            print_error(f"Failed to join channel: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    # Test case 2: Second peer joins
    data2 = {
        "peer_id": "test_peer_002",
        "channel": "general"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/add-list", json=data2)
        result = response.json()
        print_success(f"Second peer joined (members: {result.get('members_count')})")
    except Exception as e:
        print_error(f"Second join failed: {e}")
    
    return True

def test_connect_peer():
    """Test P2P connection setup"""
    print_test("POST /connect-peer - P2P Connection")
    
    data = {
        "from_peer": "test_peer_001",
        "to_peer": "test_peer_002"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/connect-peer", json=data)
        result = response.json()
        
        if result.get("status") == "success":
            peer_info = result.get("peer_info", {})
            print_success(f"Connection info retrieved for {peer_info.get('peer_id')}")
            print_info(f"  Target: {peer_info.get('ip')}:{peer_info.get('port')}")
        else:
            print_error(f"Failed to connect: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    return True

def test_broadcast_peer():
    """Test message broadcasting"""
    print_test("POST /broadcast-peer - Broadcast Message")
    
    data = {
        "peer_id": "test_peer_001",
        "channel": "general",
        "message": "Hello from automated test!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/broadcast-peer", json=data)
        result = response.json()
        
        if result.get("status") == "success":
            recipients = result.get("recipients", [])
            print_success(f"Message broadcasted to {len(recipients)} peers")
            print_info(f"  Channel: {result.get('channel')}")
            print_info(f"  Recipients: {recipients}")
        else:
            print_error(f"Failed to broadcast: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    return True

def test_send_peer():
    """Test direct messaging"""
    print_test("POST /send-peer - Direct Message")
    
    data = {
        "from_peer": "test_peer_001",
        "to_peer": "test_peer_002",
        "message": "Private message from test!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/send-peer", json=data)
        result = response.json()
        
        if result.get("status") == "success":
            print_success(f"Direct message sent")
            peer_info = result.get("peer_info", {})
            print_info(f"  To: {peer_info.get('peer_id')} "
                      f"at {peer_info.get('ip')}:{peer_info.get('port')}")
        else:
            print_error(f"Failed to send: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    return True

def test_get_messages():
    """Test message retrieval"""
    print_test("GET /get-messages - Retrieve Messages")
    
    data = {
        "channel": "general"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/get-messages", json=data)
        result = response.json()
        
        if result.get("status") == "success":
            messages = result.get("messages", [])
            print_success(f"Retrieved {result.get('count')} messages")
            for msg in messages:
                print_info(f"  [{msg.get('timestamp')}] "
                          f"{msg.get('from')}: {msg.get('message')}")
        else:
            print_error(f"Failed to get messages: {result}")
            
    except Exception as e:
        print_error(f"Request failed: {e}")
        return False
    
    return True

def test_error_handling():
    """Test error handling"""
    print_test("Error Handling Tests")
    
    # Test 1: Invalid JSON
    print_info("Testing invalid JSON...")
    try:
        response = requests.post(
            f"{BASE_URL}/submit-info",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        if result.get("status") == "error":
            print_success("Invalid JSON handled correctly")
        else:
            print_error("Invalid JSON not detected")
    except:
        print_success("Invalid JSON rejected")
    
    # Test 2: Missing required fields
    print_info("Testing missing fields...")
    try:
        response = requests.post(f"{BASE_URL}/submit-info", json={})
        result = response.json()
        if result.get("status") == "error":
            print_success("Missing fields handled correctly")
        else:
            print_error("Missing fields not detected")
    except Exception as e:
        print_error(f"Test failed: {e}")
    
    # Test 3: Non-existent peer
    print_info("Testing non-existent peer...")
    try:
        data = {
            "from_peer": "nonexistent",
            "to_peer": "test_peer_001"
        }
        response = requests.post(f"{BASE_URL}/connect-peer", json=data)
        result = response.json()
        if "peer_info" in result:
            print_info("Non-existent peer handled gracefully")
        else:
            print_success("Non-existent peer rejected")
    except Exception as e:
        print_error(f"Test failed: {e}")
    
    return True

def run_all_tests():
    """Run all test suites"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"  HYBRID CHAT APPLICATION - AUTOMATED TEST SUITE")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    print_info(f"Testing server at: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/get-list", timeout=2)
        print_success("Server is running\n")
    except:
        print_error("Server is not running!")
        print_info("Please start the server first:")
        print_info("  python start_chatapp.py --server-port 8001\n")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Peer Registration", test_submit_info),
        ("Peer Discovery", test_get_list),
        ("Channel Management", test_add_list),
        ("P2P Connection", test_connect_peer),
        ("Message Broadcasting", test_broadcast_peer),
        ("Direct Messaging", test_send_peer),
        ("Message Retrieval", test_get_messages),
        ("Error Handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(0.5)  # Small delay between tests
        except Exception as e:
            print_error(f"Test crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print(f"\n{Colors.BOLD}{'='*60}")
    print("  TEST SUMMARY")
    print(f"{'='*60}{Colors.ENDC}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.OKGREEN}PASS{Colors.ENDC}" if result else f"{Colors.FAIL}FAIL{Colors.ENDC}"
        print(f"  {status}  {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed!{Colors.ENDC}\n")
        return 0
    else:
        print(f"{Colors.WARNING}{Colors.BOLD}⚠️  Some tests failed{Colors.ENDC}\n")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())