from flask import Flask, request, jsonify
import requests
import json
import re

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_gpt_response():
    # Get the input text from the query parameter
    input_text = request.args.get('gpt4')
    
    if not input_text:
        return jsonify({'error': 'No input text provided'}), 400

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

    response = requests.post(url, data=payload, headers=headers)

    response_text = response.text

    # Use regular expressions to extract content from each chunk
    chunks = re.findall(r'"content":"(.*?)"', response_text)

    # Combine all chunks' content into one string
    combined_content = ''.join(chunks)

    return jsonify({'response': combined_content})

if __name__ == '__main__':
    app.run(debug=True)
  
