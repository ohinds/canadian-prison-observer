import multiprocessing
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 10
timeout = 100
loglevel = 'warning'
accesslog = 'gunicorn-access.log'
keepalive = 650
