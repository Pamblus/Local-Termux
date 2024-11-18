import socket
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import unquote
import os

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_content().encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        command = unquote(post_data.split('=')[1])  # Декодируем команду

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        try:
            if command.startswith('cd '):
                new_dir = command[3:].strip()
                os.chdir(new_dir)
                output = f"Changed directory to {new_dir}"
            else:
                output = subprocess.check_output(command, shell=True, text=True)
            self.wfile.write(output.encode('utf-8'))
        except Exception as e:
            self.wfile.write(f"Error: {str(e)}".encode('utf-8'))

    def get_html_content(self):
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Termux Control</title>
            <style>
                body {
                    background-color: black;
                    color: green;
                    font-family: monospace;
                    padding: 20px;
                }
                #output {
                    white-space: pre-wrap;
                    border: 1px solid green;
                    padding: 10px;
                    margin-top: 20px;
                    height: 300px;
                    overflow-y: scroll;
                }
                #command {
                    width: 100%;
                    padding: 10px;
                    margin-top: 20px;
                }
                #submit {
                    padding: 10px 20px;
                    margin-top: 10px;
                }
            </style>
        </head>
        <body>
            <h1>Termux Control</h1>
            <div id="output"></div>
            <input type="text" id="command" placeholder="Enter command">
            <button id="submit">OK</button>
            <script>
                document.getElementById('submit').addEventListener('click', function() {
                    const command = document.getElementById('command').value;
                    fetch('/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: 'command=' + encodeURIComponent(command)
                    })
                    .then(response => response.text())
                    .then(data => {
                        document.getElementById('output').innerText += '> ' + command + '\\n' + data + '\\n';
                    });
                });
            </script>
        </body>
        </html>
        """

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    port = int(input("Enter the port number to use: "))
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}...")
    print(f"Access the server at http://{get_ip()}:{port}/")
    httpd.serve_forever()

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    run()
