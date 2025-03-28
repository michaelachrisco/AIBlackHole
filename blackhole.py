from flask import Flask, request, redirect, render_template_string
import time
from collections import defaultdict
import random

app = Flask(__name__)

# Data structure to keep track of requests per IP
ip_requests = defaultdict(list)
IP_REQUEST_THRESHOLD = 1000  # Requests threshold for one hour
TIME_WINDOW = 3600  # Time window of one hour in seconds

# Function to track and limit requests based on IP
def track_requests(ip):
    current_time = time.time()
    ip_requests[ip] = [t for t in ip_requests[ip] if current_time - t < TIME_WINDOW]  # Remove old requests
    ip_requests[ip].append(current_time)
    return len(ip_requests[ip])

# Serve slow pages incrementally
@app.route('/')
def index():
    ip = request.remote_addr
    request_count = track_requests(ip)

    if request_count > IP_REQUEST_THRESHOLD:
        return serve_slow_page(request_count)
    else:
        return 'Welcome to the site!'

def serve_slow_page(request_count):
    """Serve a progressively slower page."""
    delay = min(10, request_count / 1000)  # Slow down incrementally, max 10 seconds delay
    time.sleep(delay)  # Delay to slow down the request

    # Generate the next "black hole" link
    next_page_link = f'/slow/{random.randint(1000, 9999)}'
    
    html_content = f"""
    <html>
    <head><title>Slowing You Down...</title></head>
    <body>
        <h1>You are being slowed down!</h1>
        <p>This is taking longer than usual because you're making too many requests.</p>
        <p>You have made more than {IP_REQUEST_THRESHOLD} requests in the past hour.</p>
        <p>Next step: <a href="{next_page_link}">Click here for the next page...</a></p>
    </body>
    </html>
    """
    return render_template_string(html_content)

@app.route('/slow/<int:page_id>')
def slow_page(page_id):
    ip = request.remote_addr
    request_count = track_requests(ip)

    if request_count > IP_REQUEST_THRESHOLD:
        return serve_slow_page(request_count)
    else:
        return 'Welcome back to normal!'

if __name__ == '__main__':
    app.run(debug=True)
