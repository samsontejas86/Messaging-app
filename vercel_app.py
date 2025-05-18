from wsgi import app
from flask import Flask, request

# Handler for Vercel serverless function
def handler(request):
    return app(request) 