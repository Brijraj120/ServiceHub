import os

port = int(os.environ.get("PORT", 10000))
bind = f"0.0.0.0:{port}"
workers = 2
timeout = 120
keepalive = 5
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-" 