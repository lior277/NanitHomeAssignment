"""Mock HLS streaming server with configurable network conditions.

Supports:
- GET /health
- GET /stream.m3u8
- GET /segment{1-5}.ts
- POST /control/network/              (JSON body)
- POST /control/network/<condition>   (URL path-style)
"""

from __future__ import annotations

import random
import time

from flask import Flask, jsonify, request, Response, make_response

app = Flask(__name__)

STATE = {
    "network_condition": "normal",
    "viewers": 0,
    "bitrate": 2500,
}

NETWORK_PROFILES = {
    "normal": {
        "bitrate": 2500,
        "latency": 0.05,
        "jitter": 0.01,
    },
    "poor": {
        "bitrate": 1200,
        "latency": 0.20,
        "jitter": 0.10,
    },
    "terrible": {
        "bitrate": 500,
        "latency": 0.50,
        "jitter": 0.30,
    },
}


def apply_network_delay() -> None:
    """Apply realistic delay based on the current network profile."""
    profile = NETWORK_PROFILES[STATE["network_condition"]]
    base = profile["latency"]
    jitter = random.uniform(-profile["jitter"], profile["jitter"])
    delay = max(0, base + jitter)
    time.sleep(delay)


@app.route("/health", methods=["GET"])
def health() -> Response:
    """Health check endpoint returning basic streaming metrics."""
    apply_network_delay()
    profile = NETWORK_PROFILES[STATE["network_condition"]]

    return jsonify(
        {
            "status": "healthy",
            "bitrate": STATE["bitrate"],
            "viewers": STATE["viewers"],
            "latency_ms": profile["latency"] * 1000,
            "network_condition": STATE["network_condition"],
        },
    )


@app.route("/stream.m3u8", methods=["GET"])
def stream_manifest() -> Response:
    """Return a simple HLS manifest."""
    apply_network_delay()
    manifest = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:10.0,
segment1.ts
#EXTINF:10.0,
segment2.ts
#EXTINF:10.0,
segment3.ts
#EXTINF:10.0,
segment4.ts
#EXTINF:10.0,
segment5.ts
#EXT-X-ENDLIST
"""
    return Response(manifest, mimetype="application/vnd.apple.mpegurl")


@app.route("/segment<int:num>.ts", methods=["GET"])
def segment(num: int) -> Response:
    """Return a simulated TS segment by index (1-5)."""
    if num < 1 or num > 5:
        # Always return a Response object, not a (response, status_code) tuple
        error_body = jsonify({"error": "Segment not found"})
        return make_response(error_body, 404)

    apply_network_delay()
    dummy_data = b"\x00" * (100 * 1024)
    return Response(dummy_data, mimetype="video/MP2T")


@app.route("/control/network/<condition>", methods=["POST"])
def control_network_path(condition: str) -> Response:
    """Set network condition via path (/control/network/poor)."""
    if condition not in NETWORK_PROFILES:
        resp = jsonify(
            {
                "status": "error",
                "message": f"Invalid condition. Must be one of: {list(NETWORK_PROFILES.keys())}",
            },
        )
        resp.status_code = 400
        return resp

    STATE["network_condition"] = condition
    STATE["bitrate"] = NETWORK_PROFILES[condition]["bitrate"]

    return jsonify(
        {
            "status": "success",
            "network_condition": condition,
            "bitrate": STATE["bitrate"],
        },
    )


@app.route("/control/network/", methods=["POST"])
def control_network_json() -> Response:
    """Set network condition via JSON payload: {'condition': 'poor'}."""
    data = request.get_json() or {}
    condition = data.get("condition")

    # Validate here to avoid passing None to control_network_path
    if condition not in NETWORK_PROFILES:
        resp = jsonify(
            {
                "status": "error",
                "message": f"Invalid condition. Must be one of: {list(NETWORK_PROFILES.keys())}",
            },
        )
        resp.status_code = 400
        return resp

    return control_network_path(condition)


if __name__ == "__main__":
    print("Mock streaming server starting on http://localhost:8082\n")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /stream.m3u8")
    print("  GET  /segment{1-5}.ts")
    print("  POST /control/network/<condition>")
    print("  POST /control/network/")
    print("\nNetwork conditions: normal, poor, terrible\n")

    app.run(host="0.0.0.0", port=8082, debug=False)
