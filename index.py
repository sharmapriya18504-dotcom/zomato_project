"""
Python entrypoint for Vercel deployment.
Routes standard WSGI requests through wsgi.py
"""
from wsgi import app, application, handler

__all__ = ["app", "application", "handler"]
