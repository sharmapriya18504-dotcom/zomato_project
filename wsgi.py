"""
WSGI Entrypoint for Vercel deployment.
Serves index.html and static assets (CSS, JS, data) with zero external dependencies.
"""

import os
import mimetypes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def app(environ, start_response):
    """
    Standard WSGI application handler compatible with Vercel Python runtime.
    """
    raw_path = environ.get("PATH_INFO", "/").lstrip("/")
    path = raw_path if raw_path else "index.html"
    
    file_path = os.path.join(BASE_DIR, path)
    
    # Prevent directory traversal
    try:
        real_path = os.path.abspath(file_path)
        if not real_path.startswith(BASE_DIR):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]
    except Exception:
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [b"Bad Request"]
        
    # Serve requested file
    if os.path.isfile(real_path):
        mime_type, _ = mimetypes.guess_type(real_path)
        mime_type = mime_type or "application/octet-stream"
        
        if mime_type.startswith("text/") or mime_type in ("application/javascript", "application/json"):
            headers = [("Content-Type", f"{mime_type}; charset=utf-8")]
        else:
            headers = [("Content-Type", mime_type)]
            
        start_response("200 OK", headers)
        with open(real_path, "rb") as f:
            return [f.read()]
            
    # Fallback to index.html for root or SPA paths
    index_path = os.path.join(BASE_DIR, "index.html")
    if os.path.isfile(index_path):
        start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
        with open(index_path, "rb") as f:
            return [f.read()]
            
    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"File Not Found"]


application = app
handler = app
