# Gunicorn configuration file
import multiprocessing

# Number of workers
workers = 2  # Reduced from default to save memory

# Worker class
worker_class = "gthread"

# Threads per worker
threads = 2

# Maximum requests per worker before restart
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 120

# Keep alive
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Preload application
preload_app = True

# Worker memory limits
worker_max_requests = 1000
worker_max_requests_jitter = 50

# Worker timeout
worker_timeout = 120

# Worker memory management
worker_connections = 1000
worker_class = "gthread"
threads = 2 