import requests
import json
import re
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Define headers
headers = {
    'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    'Accept-Encoding': "gzip, deflate, br, zstd",
    'Content-Type': "application/json",
    'sec-ch-ua': "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    'DNT': "1",
    'sec-ch-ua-mobile': "?1",
    'Authorization': "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImVtYWlsIjoic2lkaGFydGhtbTAyQGdtYWlsLmNvbSIsInZlcnNpb24iOjB9LCJleHBpcmUiOjE3NDAyNDEwNTExMDUsImlhdCI6MTcwODcwNTA1MSwiZXhwIjoxNzQwMjQxMDUxfQ.Po01ctOkUJJ5A4QPXeLkzCwOnb9PBta6ng0mCnGhSuQ",
    'sec-ch-ua-platform': "\"Android\"",
    'Origin': "https://start.chatgot.io",
    'Sec-Fetch-Site': "same-site",
    'Sec-Fetch-Mode': "cors",
    'Sec-Fetch-Dest': "empty",
    'Referer': "https://start.chatgot.io/",
    'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8,ja;q=0.7"
}

# Define route for the root URL
@app.route('/')
def home():
    # Serve the index.html file
    return send_file('index.html')

@app.route('/openai/gpt4', methods=['GET'])
def get_gpt_response():
    input_text = request.args.get('prompt')
    if not input_text:
        return jsonify({'error': 'No input text provided for GPT-4'}), 400

    url = "https://api.chatgot.io/api/chat/conver"

    payload = json.dumps({
        "model": {
            "id": "openai/gpt-4",
            "name": "openai/gpt-4-0125-preview",
            "title": "GPT-4",
            "prompt": "You are Chat GPT 4 , a powerful ai model developed by openai and your main goal to provide the user every information they want. Assist the user in every possible way. Here You are Powered by HRK , HRK aka HARSH is a developer.",
            "placeholder": "",
            "description": "The latest GPT-4 model, which is currently the world's most outstanding large language model, provided by OpenAI, can offer you high-quality answers in various aspects. It can return up to 4,096 output tokens and has a maximum context window of 128,000 tokens.",
            "order": 0,
            "isActived": True,
            "x": 29,
            "y": 46.9453125,
            "value": "GPT-4 128k",
            "isReplying": True
        },
        "messages": [
            {
                "role": "user",
                "content": input_text
            }
        ]
    })

    response = requests.post(url, data=payload, headers=headers)
    response_text = response.text

    # Use regular expressions to extract content from each chunk
    chunks = re.findall(r'"content":"(.*?)"', response_text)

    # Combine all chunks' content into one string
    combined_content = ''.join(chunks)

    # Adding constant response on a separate line with hyperlink
    combined_content += '\nDeveloper: Harsh (TG ID = @HRK_07)'

    # Ensure Unicode characters are not escaped
    response_dict = {'response': combined_content}
    
    return jsonify(response_dict)

@app.route('/anthropic/claudeV2', methods=['GET'])
def get_claude_response():
    input_text = request.args.get('prompt')
    if not input_text:
        return jsonify({'error': 'No input text provided for Claude v2'}), 400

    url = "https://api.chatgot.io/api/chat/conver"

    payload = json.dumps({
        "model": {
            "id": "anthropic/claude-2",
            "name": "anthropic/claude-2",
            "title": "Claude v2",
            "prompt": "You are Claude v2",
            "placeholder": "",
            "description": "Anthropic’s flagship model. Superior performance on tasks that require complex reasoning. Supports up to 100k tokens in one pass, or hundreds of pages of text.",
            "order": 0,
            "isActived": True,
            "x": 29,
            "y": 46.9453125,
            "value": "Claude v2 ",
            "isReplying": True
        },
        "messages": [
            {
                "role": "user",
                "content": input_text
            }
        ]
    })

    response = requests.post(url, data=payload, headers=headers)
    response_text = response.text

    # Use regular expressions to extract content from each chunk
    chunks = re.findall(r'"content":"(.*?)"', response_text)

    # Combine all chunks' content into one string
    combined_content = ''.join(chunks)

    # Adding constant response on a separate line with hyperlink
    combined_content += '\nDeveloper: Harsh (TG ID = @HRK_07)'

    # Ensure Unicode characters are not escaped
    response_dict = {'response': combined_content}
    
    return jsonify(response_dict)

@app.route('/openai/gpt', methods=['GET'])
def openai_endpoint():
    # Get the value of the 'prompt' query parameter
    gpt_prompt = request.args.get('prompt')

    # URL of the GPT service
    gpt_url = "https://chatgpt-online.one/wp-admin/admin-ajax.php"

    # Nonce value
    nonce = '77d60c1c19'

    try:
        # Define the data payload
        data = [
            ('_wpnonce', (None, nonce)),
            ('action', (None, 'wpaicg_chat_shortcode_message')),
            ('message', (None, gpt_prompt))
        ]

        # Define the headers
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
        }

        # Send the POST request to GPT service
        response =requests.post(gpt_url, files=data, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            json_response = response.json()
            # Extract the "data" field
            data_response = json_response.get('data')
            
            # Append developer information to the response
            data_response += '\nDeveloper: Harsh (TG ID = @HRK_07)'
            
            return jsonify({"response": data_response})
        else:
            return jsonify({"error": "Failed to send message. Status code: {}".format(response.status_code)})
    except Exception as e:
        return jsonify({"error": "An error occurred: {}".format(e)})

if __name__ == '__main__':
    # Run the Flask app on external port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

        
