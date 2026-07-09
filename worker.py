"""
RQ worker entrypoint. Run this as a separate process alongside
the FastAPI app:

    venv/bin/python worker.py

It blocks, listening on Redis for queued jobs (enqueued by the
upload route), and runs process_document() for each one.
"""

from redis import Redis
from rq import Worker, Queue

from app.core.config import settings

listen = ["default"]

if __name__ == "__main__":
    redis_conn = Redis.from_url(settings.REDIS_URL)
    queue = Queue("default", connection=redis_conn)
    worker = Worker([queue], connection=redis_conn)
    worker.work()
