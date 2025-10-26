# Configuration Gunicorn pour la production
import multiprocessing
import os

# Nombre de workers optimisé
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logs
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')

# Performance
preload_app = True
bind = f"0.0.0.0:{os.environ.get('PORT', 5000)}"

# Sécurité
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
