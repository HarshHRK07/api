import re
from mitmproxy import http, ctx, websocket

# Domains to intercept for modifying requests and corresponding keys
DOMAIN_KEYS_MAPPING = {
    "api.stripe.com": [
        rb"payment_method_data\[card\]\[cvc\]",
        rb"card\[cvc\]",
        rb"source_data\[card\]\[cvc\]"
    ],
    "cloud.boosteroid.com": [
        rb"encryptedSecurityCode\": \"(\[^\"\\\]+)"
    ],
    "api.checkout.com": [
        rb"\"cvv\": \"(\d{3,4})"
    ],
    "daisysms.com": [
        rb"\"cvc\":\"(\d{3,4})"
    ],
    # Add more domains as needed
}

def remove_cvc_from_request_body(request_body, keys_to_remove):
    """
    Removes the CVC, CVV, and encryptedSecurityCode values from the request body based on the specified keys.
    """
    for key in keys_to_remove:
        request_body = re.sub(key, b"", request_body)
    return request_body

def request(flow):
    """
    This function intercepts and modifies requests to remove CVV, CVC, and encryptedSecurityCode data.
    """
    for domain, keys in DOMAIN_KEYS_MAPPING.items():
        if domain in flow.request.pretty_host:
            if keys:
                # Log original request data for debugging
                ctx.log.info(f"Original Request Data: {flow.request.text}")
                if flow.request.websocket:
                    # For WebSocket requests, modify the raw message data
                    flow.request.websocket.messages[-1].content = remove_cvc_from_request_body(flow.request.websocket.messages[-1].content, keys)
                else:
                    # For HTTP requests, modify the request body
                    flow.request.text = remove_cvc_from_request_body(flow.request.text.encode(), keys).decode()
                # Log modified request data for debugging
                ctx.log.info(f"Modified Request Data: {flow.request.text}")
            else:
                ctx.log.info(f"Skipping request interception for domain: {domain}")

def start():
    """
    Function executed when the proxy starts
    """
    ctx.log.info("Proxy server started. Ready to intercept requests.")
    # Attach handlers to mitmproxy
    addons = [
        request
    ]
