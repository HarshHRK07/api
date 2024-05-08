import re
import json
from mitmproxy import http, ctx
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# File to store domain mappings
MAPPINGS_FILE = "domain_mappings.json"

# Initialize domain mappings with default values
DOMAIN_KEYS_MAPPING = {
    "api.stripe.com": [
        rb"payment_method_data\[card\]\[cvc\]",
        rb"card\[cvc\]",
        rb"source_data\[card\]\[cvc\]"
    ],
    "cloud.boosteroid.com": [
        rb"encryptedSecurityCode\": \"([^\"]+)\""
    ],
}

# Load existing domain mappings from file, if it exists
try:
    with open(MAPPINGS_FILE, "r") as f:
        user_mappings = json.load(f)
        DOMAIN_KEYS_MAPPING.update(user_mappings)
except FileNotFoundError:
    pass

# HTML form template with CSS styling
FORM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Domain Mapping</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
        }
        form {
            margin-top: 20px;
        }
        label {
            font-weight: bold;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 15px;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-sizing: border-box;
        }
        input[type="submit"] {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Add Domain Mapping</h1>
        <form method="POST">
            <label for="url">URL:</label><br>
            <input type="text" id="url" name="url"><br>
            <label for="cvv_regex">CVV Regex:</label><br>
            <input type="text" id="cvv_regex" name="cvv_regex"><br><br>
            <input type="submit" value="Submit">
        </form>
    </div>
</body>
</html>
"""

def save_mappings():
    """
    Save domain mappings to file.
    """
    with open(MAPPINGS_FILE, "w") as f:
        json.dump(DOMAIN_KEYS_MAPPING, f)

def remove_cvc_from_request_body(request_body, keys_to_remove):
    """
    Removes the CVC value from the request body based on the specified keys.
    """
    for key in keys_to_remove:
        request_body = re.sub(key + rb"=[\d]{3,4}", b"", request_body)
    return request_body

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

@app.route('/', methods=['GET', 'POST'])
def index():
    # Check if the client is connected to the proxy and visiting the correct URL
    if request.environ.get('HTTP_X_FORWARDED_FOR') or request.referrer != 'http://HRK':
        return "Access denied. Please connect to the proxy and visit http://HRK to add domain mappings."

    if request.method == 'POST':
        url = request.form['url']
        cvv_regex = request.form['cvv_regex']
        DOMAIN_KEYS_MAPPING[url] = [re.compile(cvv_regex.encode())]
        save_mappings()
        return "Domain mapping added successfully!"
    else:
        return render_template_string(FORM_TEMPLATE)

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
    app.run(debug=True)
  
