"""
Mock HLS streaming server with configurable network conditions.
Supports:
- GET /health
- GET /stream.m3u8
- GET /segment{1-5}.ts
- POST /control/network/              (JSON body)
- POST /control/network/<condition>   (URL path-style)
"""

import time
import random
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# --------------------------
# Server State
# --------------------------

state = {
    "network_condition": "normal",
    "viewers": 0,
    "bitrate": 2500
}

NETWORK_PROFILES = {
    "normal": {
        "bitrate": 2500,
        "latency": 0.05,
        "jitter": 0.01
    },
    "poor": {
        "bitrate": 1200,
        "latency": 0.20,
        "jitter": 0.10
    },
    "terrible": {
        "bitrate": 500,
        "latency": 0.50,
        "jitter": 0.30
    }
}


# --------------------------
# Helper Functions
# --------------------------

def apply_network_delay():
    """Apply realistic delay based on current network profile."""
    profile = NETWORK_PROFILES[state["network_condition"]]
    base = profile["latency"]
    jitter = random.uniform(-profile["jitter"], profile["jitter"])
    delay = max(0, base + jitter)
    time.sleep(delay)


# --------------------------
# Health Endpoint
# --------------------------

@app.route("/health", methods=["GET"])
def health():
    apply_network_delay()

    profile = NETWORK_PROFILES[state["network_condition"]]

    return jsonify({
        "status": "healthy",
        "bitrate": state["bitrate"],
        "viewers": state["viewers"],
        "latency_ms": profile["latency"] * 1000,  # NEW: deterministic metric
        "network_condition": state["network_condition"]
    })


# --------------------------
# HLS Manifest
# --------------------------

@app.route("/stream.m3u8", methods=["GET"])
def stream_manifest():
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


# --------------------------
# Video Segments
# --------------------------

@app.route("/segment<int:num>.ts", methods=["GET"])
def segment(num):
    """Return simulated video segment."""
    if num < 1 or num > 5:
        return jsonify({"error": "Segment not found"}), 404

    apply_network_delay()

    dummy_data = b"\x00" * (100 * 1024)  # ~100KB fake segment
    return Response(dummy_data, mimetype="video/MP2T")


# --------------------------
# Control Endpoints
# --------------------------

@app.route("/control/network/<condition>", methods=["POST"])
def control_network_path(condition):
    """Set condition via path-style endpoint (/control/network/poor)."""
    if condition not in NETWORK_PROFILES:
        return jsonify({
            "status": "error",
            "message": f"Invalid condition. Must be one of: {list(NETWORK_PROFILES.keys())}"
        }), 400

    state["network_condition"] = condition
    state["bitrate"] = NETWORK_PROFILES[condition]["bitrate"]

    return jsonify({
        "status": "success",
        "network_condition": condition,
        "bitrate": state["bitrate"]
    })


@app.route("/control/network/", methods=["POST"])
def control_network_json():
    """Set network conditions via JSON body ({"condition":"poor"})."""
    data = request.get_json() or {}
    condition = data.get("condition")

    if condition not in NETWORK_PROFILES:
        return jsonify({
            "status": "error",
            "message": f"Invalid condition. Must be one of: {list(NETWORK_PROFILES.keys())}"
        }), 400

    # Delegate to path-based logic for consistency
    return control_network_path(condition)


# --------------------------
# Startup
# --------------------------

if __name__ == "__main__":
    print("Mock streaming server starting on http://localhost:8082\n")
    print("Endpoints:")
    print("  GET  /health")
    print("  GET  /stream.m3u8")
    print("  GET  /segment{1-5}.ts")
    print("  POST /control/network/<condition>   # path-based (assignment)")
    print("  POST /control/network/              # body-based (tests)")
    print("\nNetwork conditions: normal, poor, terrible\n")

    app.run(host="0.0.0.0", port=8082, debug=False)
