from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/gpt', methods=['GET'])
def generate_response():
    try:
        prompt = request.args.get('prompt', '')
        
        url = "https://chatgptlogin.ai/chat/chat_api_stream"
        payload = {"question": prompt, "chat_id": "65d1a000c0e7117ba52d79c0", "timestamp": 9999999999}
        headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
                   'referer': "https://chatgptlogin.ai/chat/"}

        response = requests.post(url, json=payload, headers=headers)

        # Split the response into individual chunks
        chunks = response.text.split("data: ")

        # Extract the content from each chunk and concatenate them
        content = ''.join(chunk.split('"delta":')[1].split('}')[0].split(':')[-1].strip('"') for chunk in chunks if '"delta"' in chunk)

        return jsonify({"response": content})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
    
