# Gunicorn production configuration

bind = "0.0.0.0:8000"

workers = 2
threads = 4

worker_class = "gthread"

timeout = 120
keepalive = 5

errorlog = "-"
accesslog = "-"
loglevel = "info"

process_name = "gunicorn predictions"

# Grant access to the Unix socket
graceful_timeout = 30
