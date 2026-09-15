from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

from modules.intraday_zerodha_auth import (
    save_request_token,
)


class KiteAuthCallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        request_token = query_params.get(
            "request_token",
            [None]
        )[0]

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html"
        )
        self.end_headers()

        if request_token:

            saved = save_request_token(
                request_token
            )

            if saved:
                message = """
                <html>
                    <body>
                        <h2>JKJ AI Trader</h2>
                        <p>Kite authentication callback received successfully.</p>
                        <p>Authentication token received securely.</p>
                        <p>You may return to JKJ AI Trader.</p>
                    </body>
                </html>
                """
            else:
                message = """
                <html>
                    <body>
                        <h2>JKJ AI Trader</h2>
                        <p>Authentication callback received.</p>
                        <p>Token could not be stored.</p>
                    </body>
                </html>
                """

        else:

            message = """
            <html>
                <body>
                    <h2>JKJ AI Trader</h2>
                    <p>Callback endpoint is working.</p>
                    <p>No request token was supplied.</p>
                </body>
            </html>
            """

        self.wfile.write(
            message.encode("utf-8")
        )

    def log_message(self, format, *args):
        print(
            "Kite Callback:",
            format % args
        )


if __name__ == "__main__":

    server = HTTPServer(
        ("0.0.0.0", 8000),
        KiteAuthCallbackHandler
    )

    print(
        "JKJ Kite authentication callback "
        "running on port 8000"
    )

    print(
        "Waiting for Zerodha authentication "
        "callback..."
    )

    try:
        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\nJKJ Kite authentication callback "
            "stopped."
        )