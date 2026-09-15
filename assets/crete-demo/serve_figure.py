"""Serve only the live demo Hubble image to the local slide preview."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.home() / 'forth-demo')
    parser.add_argument('--port', type=int, default=4203)
    args = parser.parse_args()
    figure = args.root.expanduser() / 'results/hubble_diagram.png'

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if urlsplit(self.path).path != '/results/hubble_diagram.png':
                self.send_error(404)
                return
            try:
                data = figure.read_bytes()
            except FileNotFoundError:
                self.send_error(404, 'Waiting for demo figure')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *_):
            pass

    print(f'Watching {figure} on http://127.0.0.1:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
