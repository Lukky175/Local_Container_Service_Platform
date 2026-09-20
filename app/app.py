from flask import Flask, jsonify, render_template, Response
import os
import socket
import time

from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

CONTAINER_ID = os.getenv("CONTAINER_ID", "unknown")


# Prometheus metric
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "container"]
)


@app.before_request
def track_request():
    from flask import request

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        container=CONTAINER_ID
    ).inc()


@app.route("/")
def home():
    return render_template(
        "index.html",
        container_id=CONTAINER_ID,
        hostname=socket.gethostname()
    )


@app.route("/api")
def api():
    return jsonify({
        "service": "dummy-service",
        "container": CONTAINER_ID,
        "hostname": socket.gethostname(),
        "status": "running",
        "timestamp": time.time()
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "container": CONTAINER_ID
    }), 200


@app.route("/metrics")
def metrics():
    return Response(
        generate_latest(),
        mimetype=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)