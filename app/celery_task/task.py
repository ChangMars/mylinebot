import time

from mylinebot.celery import app

@app.task
def sendnotify():
    print("上漲0000")


@app.task
def add(x, y):
    print("asdasdasdasdasdasdsad")
    time.sleep(5)
    print(x + y)