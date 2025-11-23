# tests/test_stream_quality.py
"""
Stage 2 – Streaming validation on API layer.

Precondition (local):
    python mock_services/mock_stream_server.py
"""

import pytest

from config.config import StreamingConfig
from infra.streaming_validator import StreamingValidator


@pytest.mark.streaming
def test_stream_latency_degrades_from_normal_to_poor(streaming_validator: StreamingValidator) -> None:
    v = streaming_validator

    # Baseline
    v.set_network_condition("normal")
    normal_latency = v.get_latency_ms()
    manifest_normal = v.get_manifest()
    assert "#EXTM3U" in manifest_normal

    # Poor network
    v.set_network_condition("poor")
    poor_latency = v.get_latency_ms()
    manifest_poor = v.get_manifest()
    assert "#EXTM3U" in manifest_poor

    assert poor_latency > normal_latency, (
        f"Expected higher latency under 'poor' network, "
        f"got normal={normal_latency}, poor={poor_latency}"
    )


@pytest.mark.streaming
@pytest.mark.parametrize("condition", ["normal", "poor", "terrible"])
def test_manifest_available_under_all_conditions(
    streaming_validator: StreamingValidator,
    condition: str,
) -> None:
    v = streaming_validator
    v.set_network_condition(condition)
    manifest = v.get_manifest()
    assert "#EXTM3U" in manifest


@pytest.mark.streaming
def test_segments_reachable_under_normal_conditions(
    streaming_validator: StreamingValidator,
) -> None:
    v = streaming_validator
    v.set_network_condition("normal")

    for i in range(1, 6):
        data = v.get_segment(i)
        assert len(data) > 0, f"Segment {i} should not be empty"


@pytest.mark.streaming
def test_invalid_segment_returns_error_code(
    streaming_config: StreamingConfig,
) -> None:
    """Example negative test – not using validator, just raw HTTP if desired."""
    import requests

    resp = requests.get(f"{streaming_config.base_url.rstrip('/')}/segment0.ts", timeout=streaming_config.timeout)
    assert resp.status_code == 404
