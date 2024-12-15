from http.server import BaseHTTPRequestHandler, HTTPServer
from jinja2 import Environment, FileSystemLoader
import os
import json
import urllib.parse

PORT = 8000

env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class RequestHandler(BaseHTTPRequestHandler):

    def render_template(self, template_name, **context):

        template = env.get_template(template_name)
        content = template.render(context)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def load_doors_from_json(self, json_file_path):

        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return data.get('doors', [])
        except Exception as e:
            self.send_error(500, "Error reading data file")
            return []

    def do_GET(self):
        root = os.path.dirname(os.path.abspath(__file__))
        try:
            if self.path == '/':
                self.render_template('index.html')
            elif self.path == '/doors':
                json_file_path = os.path.join(root, 'data.json')
                door_list = self.load_doors_from_json(json_file_path)
                self.render_template('doors.html', door_list=door_list)
            elif self.path == '/contact':
                self.render_template('contact.html', message_sent=False)
            elif self.path.startswith('/static/'):
                file_path = root + self.path
                self.serve_static_file(file_path)
            else:
                self.send_error(404, "Page Not Found")
        except Exception as e:
            self.send_error(500, "Internal Server Error")

    def do_POST(self):
        if self.path == '/contact':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            post_data = urllib.parse.parse_qs(post_data)

            name = post_data.get('name', [''])[0]
            message = post_data.get('message', [''])[0]


            self.render_template('contact.html', message_sent=True, name=name)
        else:
            self.send_error(404, "Page Not Found")

    def serve_static_file(self, file_path):

        try:
            with open(file_path, 'rb') as file:
                self.send_response(200)
                if file_path.endswith('.css'):
                    mime_type = 'text/css'
                elif file_path.endswith('.js'):
                    mime_type = 'application/javascript'
                else:
                    mime_type = 'application/octet-stream'
                self.send_header('Content-type', mime_type)
                self.end_headers()
                self.wfile.write(file.read())
        except IOError:
            self.send_error(404, "File Not Found")

def run(server_class=HTTPServer, handler_class=RequestHandler, port=PORT):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()