from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from html import escape


class LabRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        request = urlparse(self.path)
        parameters = parse_qs(request.query)
        search_term = parameters.get("q", [""])[0]

        if request.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
            return

        if request.path not in ["/", "/search"]:
            self.send_error(404, "Page not found")
            return

        safe_search_term = escape(search_term)

        page = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Alia WAF Operations Lab</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 760px;
                    margin: 60px auto;
                    padding: 25px;
                    background: #f4f6f8;
                }}
                main {{
                    background: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.12);
                }}
                input {{
                    width: 70%;
                    padding: 10px;
                }}
                button {{
                    padding: 10px 18px;
                    cursor: pointer;
                }}
                .result {{
                    margin-top: 25px;
                    padding: 15px;
                    background: #eef3f7;
                }}
            </style>
        </head>
        <body>
            <main>
                <h1>WAF Security Operations Lab</h1>
                <p>This safe test application is protected by Cloudflare.</p>

                <form action="/search" method="GET">
                    <label for="q">Search the training catalog:</label><br><br>
                    <input id="q" name="q" type="text"
                           placeholder="Example: SQL fundamentals">
                    <button type="submit">Search</button>
                </form>

                <div class="result">
                    <strong>Search received:</strong> {safe_search_term}
                </div>
            </main>
        </body>
        </html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8000), LabRequestHandler)
    print("WAF lab application running at http://127.0.0.1:8000")
    server.serve_forever()