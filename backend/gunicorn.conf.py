import multiprocessing

# Gunicorn config variables
workers = 1  # Keep only one worker to reduce memory usage
threads = 2
timeout = 300  # Increased timeout for dataset loading
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
worker_class = "sync"
bind = "0.0.0.0:10000"
worker_tmp_dir = "/dev/shm"  # Use shared memory for worker temp files
preload_app = True  # Preload the application to share memory between workers
max_requests = 1000  # Restart workers after 1000 requests
max_requests_jitter = 50  # Add some randomness to prevent all workers from restarting at once

# Memory settings
worker_connections = 1000
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190