from http.server import BaseHTTPRequestHandler
import json
import os
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        api_key = os.environ.get('ASTRO_API_KEY')
        if not api_key:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Missing API key')
            return

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }

        api_url = 'https://json.freeastrologyapi.com/western/planets'

        try:
            resp = requests.post(api_url, headers=headers, json=data)
            resp.raise_for_status()
            result = resp.json()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())