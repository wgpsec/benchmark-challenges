#!/usr/bin/env python3
"""
APEX-016-25: Vulnerable HTTP Reverse Proxy

This proxy is intentionally VULNERABLE to CL.TE request smuggling.

VULNERABILITY:
- The proxy uses Content-Length to determine request boundaries
- It forwards the Transfer-Encoding header without processing it
- The backend (Node.js) processes Transfer-Encoding: chunked
- This creates a desync where the proxy reads CL bytes, but backend
  processes chunked encoding, treating leftover bytes as a new request

This simulates a vulnerable load balancer or reverse proxy that doesn't
properly handle requests with conflicting Content-Length and Transfer-Encoding.
"""

import socket
import threading
import re
import os
import sys

BACKEND_HOST = os.environ.get('BACKEND_HOST', 'backend')
BACKEND_PORT = int(os.environ.get('BACKEND_PORT', '3000'))
LISTEN_PORT = int(os.environ.get('LISTEN_PORT', '80'))

# Admin paths that should be blocked by proxy (but can be bypassed via smuggling)
BLOCKED_PATHS = ['/admin', '/admin/', '/admin/flag', '/admin/users', '/admin/config']

# Connection pool for backend (maintains persistent connections)
backend_pool = []
pool_lock = threading.Lock()


def log(msg):
    """Thread-safe logging with flush"""
    print(f"[PROXY] {msg}", flush=True)


def parse_headers(data):
    """Parse HTTP headers from raw data"""
    lines = data.split(b'\r\n')
    headers = {}

    for line in lines[1:]:
        if line == b'':
            break
        if b':' in line:
            key, value = line.split(b':', 1)
            headers[key.strip().lower()] = value.strip()

    return headers


def get_request_line(data):
    """Extract request line (method, path, version)"""
    first_line = data.split(b'\r\n')[0].decode('utf-8', errors='ignore')
    parts = first_line.split(' ')
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None


def is_blocked_path(path):
    """Check if path should be blocked"""
    if path is None:
        return False
    for blocked in BLOCKED_PATHS:
        if path.startswith(blocked):
            return True
    return False


def get_backend_connection():
    """Get or create a backend connection (persistent connections)"""
    with pool_lock:
        if backend_pool:
            return backend_pool.pop()

    # Create new connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((BACKEND_HOST, BACKEND_PORT))
    return sock


def return_backend_connection(sock):
    """Return connection to pool"""
    with pool_lock:
        if len(backend_pool) < 10:
            backend_pool.append(sock)
        else:
            sock.close()


def read_http_response(sock):
    """Read a complete HTTP response"""
    response = b''

    # Read headers
    sock.settimeout(5)
    while b'\r\n\r\n' not in response:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                log(f"read_http_response: connection closed, got {len(response)} bytes")
                return response
            response += chunk
        except socket.timeout:
            log(f"read_http_response: timeout waiting for headers")
            return response

    # Parse headers to find Content-Length
    header_end = response.find(b'\r\n\r\n') + 4
    headers_part = response[:header_end]

    # Check for Content-Length
    content_length = 0
    for line in headers_part.split(b'\r\n'):
        if line.lower().startswith(b'content-length:'):
            content_length = int(line.split(b':')[1].strip())
            break

    # Check for chunked encoding
    is_chunked = b'transfer-encoding: chunked' in headers_part.lower()

    if content_length > 0:
        # Read body based on Content-Length
        body_received = len(response) - header_end
        while body_received < content_length:
            chunk = sock.recv(min(4096, content_length - body_received))
            if not chunk:
                break
            response += chunk
            body_received += len(chunk)
    elif is_chunked:
        # Read chunked body until 0\r\n\r\n
        while not response.endswith(b'0\r\n\r\n'):
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk

    return response


def handle_client(client_socket, client_addr):
    """
    Handle a single client connection.

    VULNERABLE BEHAVIOR:
    - Uses Content-Length to determine how much data to read
    - Forwards Transfer-Encoding header as-is to backend
    - Does NOT process chunked encoding
    - Uses persistent backend connections (enables smuggling)

    This allows CL.TE smuggling when both headers are present.
    """
    try:
        # Read request data
        request_data = b''
        client_socket.settimeout(5)

        # Read headers first
        while b'\r\n\r\n' not in request_data:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            request_data += chunk

        if not request_data:
            client_socket.close()
            return

        # Parse headers
        headers = parse_headers(request_data)
        method, path = get_request_line(request_data)

        log(f"{client_addr} -> {method} {path}")

        # Check if path is blocked (security control we'll bypass)
        if is_blocked_path(path):
            log(f"BLOCKED: {path}")
            response = b'HTTP/1.1 403 Forbidden\r\n'
            response += b'Content-Type: application/json\r\n'
            response += b'Connection: close\r\n'
            response += b'\r\n'
            response += b'{"error": "Admin access forbidden"}'
            client_socket.sendall(response)
            client_socket.close()
            return

        # VULNERABLE: Use Content-Length to determine body size
        # We ignore Transfer-Encoding header here but pass it to backend!
        content_length = int(headers.get(b'content-length', b'0'))

        # Calculate how much body we've already received
        header_end = request_data.find(b'\r\n\r\n') + 4
        body_received = len(request_data) - header_end

        # Read remaining body based on Content-Length
        while body_received < content_length:
            remaining = content_length - body_received
            chunk = client_socket.recv(min(4096, remaining))
            if not chunk:
                break
            request_data += chunk
            body_received += len(chunk)

        log(f"Read {len(request_data)} bytes total (CL: {content_length})")
        log(f"Request data: {repr(request_data[:200])}")

        # Create fresh backend connection for each request
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.settimeout(10)
        try:
            backend_socket.connect((BACKEND_HOST, BACKEND_PORT))
            log(f"Connected to backend {BACKEND_HOST}:{BACKEND_PORT}")
        except Exception as e:
            log(f"Failed to connect to backend: {e}")
            error_resp = b'HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n'
            client_socket.sendall(error_resp)
            return

        try:
            # Forward to backend (including Transfer-Encoding header!)
            # The key vulnerability: backend sees ALL data including smuggled request
            log(f"About to send {len(request_data)} bytes to backend")
            backend_socket.sendall(request_data)
            log(f"Sent {len(request_data)} bytes to backend")

            # Read FIRST response from backend
            log(f"About to read response from backend")
            response = read_http_response(backend_socket)
            log(f"Received {len(response)} bytes from backend")

            # VULNERABILITY: If backend processed chunked encoding and saw
            # a smuggled request, it will send TWO responses. We only read
            # the first one. But on a persistent connection, the second
            # response would be returned to the NEXT client request!

            # For this benchmark, let's also read a second response if available
            # to demonstrate the vulnerability immediately
            # Give backend time to process the smuggled request and send second response
            backend_socket.settimeout(2)
            try:
                extra = b''
                # Keep reading until we get the complete second response or timeout
                while True:
                    try:
                        chunk = backend_socket.recv(4096)
                        if not chunk:
                            break
                        extra += chunk
                        log(f"Got extra chunk: {len(chunk)} bytes")
                        # Reset timeout for more data
                        backend_socket.settimeout(0.5)
                    except socket.timeout:
                        break
                if extra:
                    log(f"Extra data from backend: {len(extra)} bytes")
                    log(f"Extra data content: {repr(extra[:500])}")
                    response += extra
            except socket.timeout:
                log(f"No extra data (timeout)")
                pass

            # Close backend connection
            backend_socket.close()

            # Send response to client
            client_socket.sendall(response)
            log(f"Sent {len(response)} bytes to client")

        except Exception as e:
            log(f"Backend error: {e}")
            try:
                backend_socket.close()
            except:
                pass
            # Send error response
            error_resp = b'HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n'
            client_socket.sendall(error_resp)

    except Exception as e:
        log(f"Error: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass


def main():
    log(f"Starting vulnerable CL.TE proxy on port {LISTEN_PORT}")
    log(f"Backend: {BACKEND_HOST}:{BACKEND_PORT}")
    log(f"VULNERABLE: Using Content-Length, passing Transfer-Encoding")
    log(f"Blocked paths: {BLOCKED_PATHS}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(10)

    log(f"Listening on 0.0.0.0:{LISTEN_PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    main()
