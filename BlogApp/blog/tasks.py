import time

from BlogApp.celery import app


@app.task(bind=True)
def add(self, a: int, b: int):
    print(a + b)
    return a + b
