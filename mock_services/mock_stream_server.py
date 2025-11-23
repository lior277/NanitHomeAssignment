"""Mock HLS streaming server with configurable network conditions."""

import json
import time
import random
from flask import Flask, jsonify, request, Response

app = Flask(__name__)

# Server state
state = {
    "network_condition": "normal",
    "viewers": 0,
    "bitrate": 2500
}

# Network condition profiles
NETWORK_PROFILES = {
    "normal": {
        "bitrate": 2500,
        "latency": 0.05,
        "jitter": 0.01
    },
    "poor": {
        "bitrate": 1200,
        "latency": 0.2,
        "jitter": 0.1
    },
    "terrible": {
        "bitrate": 500,
        "latency": 0.5,
        "jitter": 0.3
    }
}


def apply_network_delay():
    """Apply network delay based on current condition."""
    profile = NETWORK_PROFILES[state["network_condition"]]
    delay = profile["latency"] + random.uniform(-profile["jitter"], profile["jitter"])
    time.sleep(max(0, delay))


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    apply_network_delay()

    return jsonify({
        "status": "healthy",
        "bitrate": state["bitrate"],
        "viewers": state["viewers"],
        "network_condition": state["network_condition"]
    })


@app.route("/stream.m3u8", methods=["GET"])
def stream_manifest():
    """Return HLS manifest."""
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
def segment(num):
    """Return video segment."""
    if num < 1 or num > 5:
        return jsonify({"error": "Segment not found"}), 404

    apply_network_delay()

    # Simulate video segment
    segment_size = 100 * 1024  # 100KB
    dummy_data = b"\x00" * segment_size

    return Response(dummy_data, mimetype="video/MP2T")


@app.route("/control/network/", methods=["POST"])
def control_network():
    """Set network conditions."""
    data = request.get_json()
    condition = data.get("condition")

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


if __name__ == "__main__":
    print("Mock streaming server starting on http://localhost:8082")
    print("\nEndpoints:")
    print("  GET  /health")
    print("  GET  /stream.m3u8")
    print("  GET  /segment{1-5}.ts")
    print("  POST /control/network/")
    print("\nNetwork conditions: normal, poor, terrible\n")

    app.run(host="0.0.0.0", port=8082, debug=False)