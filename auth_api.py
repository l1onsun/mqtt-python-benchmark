from http.server import BaseHTTPRequestHandler, HTTPServer


class Server(BaseHTTPRequestHandler):
    def do_POST(self):
        self.send_response(200)
        # self.send_header("Content-type", "text/html")
        self.end_headers()


if __name__ == "__main__":
    print("Starting auth_api on port: 80")
    HTTPServer(('', 80), Server).serve_forever()
