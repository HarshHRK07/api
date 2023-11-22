from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/api/v1/ai/chat/completions/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    target_url = 'https://api.voidevs.com/v1/ai/chat/completions/' + path
    headers = {key: value for (key, value) in request.headers if key != 'Host'}

    if request.method == 'GET':
        response = requests.get(target_url, headers=headers)
    elif request.method == 'POST':
        response = requests.post(target_url, data=request.get_data(), headers=headers)
    else:
        return jsonify({'error': 'Unsupported HTTP method'}), 500

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]

    return jsonify(content=response.json(), headers=headers), response.status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
  
