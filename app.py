"""
Zomato Restaurant Cost Clustering & Intelligence Platform
Author: Priya Sharma
Web UI & WSGI Application Entrypoint (Vercel & Local Server)
"""

import os
from wsgi import app, application, handler

__all__ = ["app", "application", "handler"]

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8501))
    print(f"🚀 Starting Zomato Intelligence Platform on http://localhost:{port}")
    with make_server("0.0.0.0", port, app) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")