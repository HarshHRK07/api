import json
import re
from mitmproxy import ctx, http, websocket

def load_domain_keys_mapping(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

DOMAIN_KEYS_MAPPING = load_domain_keys_mapping("demo.json")

def remove_cvc_from_request_body(request_body, keys_to_remove):
    """
    Removes the CVC, CVV, and encryptedSecurityCode values from the request body based on the specified keys.
    """
    for key in keys_to_remove:
        request_body = re.sub(key.encode(), b"", request_body)
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
                if flow.websocket:
                    # For WebSocket requests, modify the raw message data
                    for message in flow.websocket.messages:
                        message.content = remove_cvc_from_request_body(message.content, keys)
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
    
