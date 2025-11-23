"""
Mock Streaming Server for Testing Automation Infrastructure

This server simulates an HLS streaming service with configurable network conditions
to test automation and monitoring systems.
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime
from threading import Lock

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Server start time for uptime calculation
SERVER_START_TIME = time.time()

# Thread-safe lock for state management
state_lock = Lock()

# Network condition configurations
NETWORK_CONDITIONS = {
    "normal": {
        "packet_loss": 0.0,
        "latency_ms": 10,
        "jitter_ms": 5,
        "description": "Normal network (stable connection)"
    },
    "poor": {
        "packet_loss": 0.15,
        "latency_ms": 200,
        "jitter_ms": 50,
        "description": "Poor network (mobile 3G-like)"
    },
    "terrible": {
        "packet_loss": 0.15,
        "latency_ms": 500,
        "jitter_ms": 150,
        "description": "Terrible network (congested/unstable)"
    }
}

# Current network condition (default: normal)
current_condition = "normal"


def apply_network_effects(endpoint_type: str = "default") -> Optional[Tuple[int, str]]:
    """
    Apply network effects based on current condition.
    
    Args:
        endpoint_type: Type of endpoint ("manifest", "segment", "health", or "default")
        
    Returns:
        None if request succeeds, or (status_code, error_message) tuple if it fails
    """
    with state_lock:
        condition = NETWORK_CONDITIONS[current_condition]
    
    # Check for packet loss
    if random.random() < condition["packet_loss"]:
        # Different endpoints return different error codes on packet loss
        if endpoint_type == "manifest":
            logger.warning(f"Packet loss simulated for manifest request (504)")
            return (504, "Gateway Timeout")
        else:
            logger.warning(f"Packet loss simulated for {endpoint_type} request (503)")
            return (503, "Service Unavailable")
    
    # Calculate delay with jitter
    base_latency = condition["latency_ms"] / 1000.0  # Convert to seconds
    jitter = condition["jitter_ms"] / 1000.0
    delay = base_latency + random.uniform(-jitter, jitter)
    delay = max(0, delay)  # Ensure non-negative delay
    
    # Apply delay
    if delay > 0:
        time.sleep(delay)
    
    logger.debug(f"Request processed with {delay*1000:.1f}ms delay")
    return None


def get_uptime() -> int:
    """Get server uptime in seconds."""
    return int(time.time() - SERVER_START_TIME)


def get_random_viewers() -> int:
    """Generate realistic viewer count."""
    # Base viewer count varies by time, with some randomness
    base = random.randint(20, 80)
    return base


def get_hls_manifest() -> str:
    """
    Generate HLS manifest file content.
    
    Returns:
        String containing valid HLS .m3u8 manifest
    """
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
    return manifest


def get_fake_video_segment() -> bytes:
    """
    Generate fake video segment data.
    
    Returns:
        Bytes object containing ~10KB of fake video data
    """
    # Generate approximately 10KB of fake data
    segment_data = b"FAKE_VIDEO_DATA_SEGMENT_"
    return segment_data


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation."""
    # Control endpoints never experience network effects
    
    documentation = {
        "service": "Mock Streaming Server",
        "version": "1.0.0",
        "description": "HLS streaming simulation with network condition controls",
        "current_network_condition": current_condition,
        "endpoints": {
            "streaming": {
                "GET /stream.m3u8": "HLS manifest file",
                "GET /segment<N>.ts": "Video segment (N = 1-5)"
            },
            "monitoring": {
                "GET /health": "Health check with streaming metrics",
                "GET /metrics": "Detailed performance statistics"
            },
            "control": {
                "GET /control/network/<condition>": "Set network condition (normal|poor|terrible)",
                "GET /control/network/current": "Get current network condition"
            }
        },
        "available_conditions": list(NETWORK_CONDITIONS.keys()),
        "documentation": "See README.md for complete API documentation"
    }
    
    return jsonify(documentation), 200


@app.route('/stream.m3u8', methods=['GET'])
def get_manifest():
    """Serve HLS manifest file."""
    logger.info("Manifest requested")
    
    # Apply network effects
    error = apply_network_effects("manifest")
    if error:
        status_code, message = error
        return Response(message, status=status_code)
    
    # Generate and return manifest
    manifest_content = get_hls_manifest()
    logger.info("Manifest served successfully")
    
    return Response(
        manifest_content,
        mimetype='application/vnd.apple.mpegurl',
        status=200
    )


@app.route('/segment<int:segment_num>.ts', methods=['GET'])
def get_segment(segment_num: int):
    """
    Serve video segment.
    
    Args:
        segment_num: Segment number (1-5)
    """
    logger.info(f"Segment {segment_num} requested")
    
    # Validate segment number
    if segment_num < 1 or segment_num > 5:
        logger.warning(f"Invalid segment number requested: {segment_num}")
        return Response("Invalid segment number. Must be 1-5.", status=400)
    
    # Apply network effects
    error = apply_network_effects("segment")
    if error:
        status_code, message = error
        return Response(message, status=status_code)
    
    # Generate and return fake video data
    segment_data = get_fake_video_segment()
    logger.info(f"Segment {segment_num} served successfully ({len(segment_data)} bytes)")
    
    return Response(
        segment_data,
        mimetype='video/mp2t',
        status=200
    )


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint with streaming metrics."""
    logger.info("Health check requested")
    
    # Apply network effects
    error = apply_network_effects("health")
    if error:
        status_code, message = error
        return Response(message, status=status_code)
    
    # Generate health response
    health_data = {
        "status": "streaming",
        "bitrate": "1080p",
        "viewers": get_random_viewers(),
        "uptime_seconds": get_uptime(),
        "network_condition": current_condition,
        "timestamp": time.time()
    }
    
    logger.info(f"Health check successful - {health_data['viewers']} viewers")
    return jsonify(health_data), 200


@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Detailed performance metrics endpoint."""
    logger.info("Metrics requested")
    
    # Apply network effects
    error = apply_network_effects("metrics")
    if error:
        status_code, message = error
        return Response(message, status=status_code)
    
    # Get current condition details
    with state_lock:
        condition_settings = NETWORK_CONDITIONS[current_condition].copy()
    
    # Generate detailed metrics
    metrics_data = {
        "server": {
            "uptime_seconds": get_uptime(),
            "start_time": SERVER_START_TIME,
            "current_time": time.time()
        },
        "streaming": {
            "status": "active",
            "bitrate": "1080p",
            "fps": 30,
            "viewers": get_random_viewers(),
            "segments_available": 5
        },
        "network": {
            "current_condition": current_condition,
            "settings": condition_settings
        },
        "performance": {
            "average_latency_ms": condition_settings["latency_ms"],
            "jitter_ms": condition_settings["jitter_ms"],
            "packet_loss_rate": condition_settings["packet_loss"]
        }
    }
    
    logger.info("Metrics served successfully")
    return jsonify(metrics_data), 200


@app.route('/control/network/<condition>', methods=['PUT'])
def set_network_condition(condition: str):
    """
    Set network condition.
    
    Args:
        condition: Network condition name (normal, poor, terrible)
    """
    global current_condition
    
    # Control endpoints never experience network effects
    logger.info(f"Network condition change requested: {condition}")
    
    # Validate condition
    if condition not in NETWORK_CONDITIONS:
        logger.warning(f"Invalid network condition requested: {condition}")
        return jsonify({
            "error": "Invalid network condition",
            "valid_conditions": list(NETWORK_CONDITIONS.keys())
        }), 400
    
    # Update condition
    with state_lock:
        current_condition = condition
        settings = NETWORK_CONDITIONS[condition].copy()
    
    logger.info(f"Network condition changed to: {condition}")
    
    response = {
        "applied": condition,
        "settings": {
            "packet_loss": settings["packet_loss"],
            "latency_ms": settings["latency_ms"],
            "jitter_ms": settings["jitter_ms"],
            "description": settings["description"]
        }
    }
    
    return jsonify(response), 200


@app.route('/control/network/current', methods=['GET'])
def get_current_condition():
    """Get current network condition."""
    # Control endpoints never experience network effects
    logger.info("Current network condition requested")
    
    with state_lock:
        condition = current_condition
        settings = NETWORK_CONDITIONS[condition].copy()
    
    response = {
        "current_condition": condition,
        "settings": {
            "packet_loss": settings["packet_loss"],
            "latency_ms": settings["latency_ms"],
            "jitter_ms": settings["jitter_ms"],
            "description": settings["description"]
        }
    }
    
    return jsonify(response), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        "error": "Endpoint not found",
        "message": "See GET / for API documentation"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "message": "An unexpected error occurred"
    }), 500


if __name__ == '__main__':
    logger.info("Starting Mock Streaming Server...")
    logger.info(f"Initial network condition: {current_condition}")
    logger.info("Server will listen on http://0.0.0.0:8082")
    
    # Run server with threading enabled for concurrent requests
    app.run(
        host='0.0.0.0',
        port=8082,
        debug=False,
        threaded=True
    )

