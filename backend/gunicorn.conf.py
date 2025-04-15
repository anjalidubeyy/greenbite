import multiprocessing

# Gunicorn config variables
workers = 1
threads = 2
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
worker_class = "sync"
bind = "0.0.0.0:10000" 