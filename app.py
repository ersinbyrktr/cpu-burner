# app.py
from flask import Flask, request
import time
import threading

app = Flask(__name__)

def burn_cpu(seconds):
    end = time.time() + seconds
    while time.time() < end:
        pass  # busy wait

@app.route("/cpu")
def cpu():
    duration = float(request.args.get("duration", 1))  # seconds
    threads = int(request.args.get("threads", 1))
    jobs = []

    for _ in range(threads):
        t = threading.Thread(target=burn_cpu, args=(duration,))
        jobs.append(t)
        t.start()

    for job in jobs:
        job.join()

    return f"Burned CPU for {duration} seconds with {threads} threads."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
