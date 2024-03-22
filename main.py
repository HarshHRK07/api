import requests
import json
import re
from flask import Flask, request, jsonify, send_file, redirect, send_from_directory, after_this_request
from pytube import YouTube
import os
import uuid

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
        stream = yt.streams.filter(only_audio=True).first()
    elif format == 'mp4':
        stream = yt.streams.filter(only_video=True).first()
    else:
        return "Invalid format. Use 'mp3' or 'mp4'", 400

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

    chunks = re.findall(r'"content":"(.*?)"', response_text)
    combined_content = ''.join(chunks)
    combined_content += '\nDeveloper: Harsh (TG ID = @HRK_07)'

    response_dict = {'response': combined_content}
    
    return jsonify(response_dict)

@app.route('/openai/gpt', methods=['GET'])
def openai_endpoint():
    gpt_prompt = request.args.get('prompt')
    gpt_url = "https://chatgpt-online.one/wp-admin/admin-ajax.php"
    nonce = '77d60c1c19'

    try:
        data = [
            ('_wpnonce', (None, nonce)),
            ('action', (None, 'wpaicg_chat_shortcode_message')),
            ('message', (None, gpt_prompt))
        ]

        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36"
        }

        response = requests.post(gpt_url, files=data, headers=headers)

        if response.status_code == 200:
            json_response = response.json()
            data_response = json_response.get('data')
            data_response += '\nDeveloper: Harsh (TG ID = @HRK_07)'
            
            return jsonify({"response": data_response})
        else:
            return jsonify({"error": "Failed to send message. Status code: {}".format(response.status_code)})
    except Exception as e:
        return jsonify({"error": "An error occurred: {}".format(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
    
