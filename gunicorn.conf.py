import os

# Render binds external traffic to $PORT on 0.0.0.0 (defaults to 10000 on Render)
port = os.environ.get("PORT", "10000")
bind = f"0.0.0.0:{port}"

# Concurrency & Worker configuration
workers = int(os.environ.get("WEB_CONCURRENCY", "1"))
threads = 4
timeout = 120
keepalive = 5

# Logging to stdout/stderr for Render log stream
accesslog = "-"
errorlog = "-"
loglevel = "info"
