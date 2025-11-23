"""Tests for streaming quality behavior under different conditions."""

from __future__ import annotations

import os

import pytest

from infra.streaming.streaming_validator import StreamingValidator


@pytest.mark.streaming
def test_stream_latency_degrades_from_normal_to_poor(
    streaming_validator: StreamingValidator,
) -> None:
    """Latency should increase when network degrades from normal to poor."""
    validator = streaming_validator

    validator.set_network_condition("normal")
    normal_latency = validator.get_latency_ms()

    validator.set_network_condition("poor")
    poor_latency = validator.get_latency_ms()

    assert poor_latency > normal_latency, (
        "Expected latency under 'poor' network to be higher than 'normal'. "
        f"Got normal={normal_latency}, poor={poor_latency}"
    )


@pytest.mark.streaming
@pytest.mark.parametrize("condition", ["normal", "poor", "terrible"])
def test_manifest_available_under_all_conditions(
    streaming_validator: StreamingValidator,
    condition: str,
) -> None:
    """Manifest should be available for all declared network conditions."""
    validator = streaming_validator
    validator.set_network_condition(condition)
    manifest = validator.get_manifest()
    assert "#EXTM3U" in manifest


@pytest.mark.streaming
def test_segments_reachable_under_normal_conditions(
    streaming_validator: StreamingValidator,
) -> None:
    """Segments 1-5 should be reachable under normal network conditions."""
    validator = streaming_validator
    validator.set_network_condition("normal")

    for index in range(1, 6):
        data = validator.get_segment(index)
        assert data, f"Segment {index} should not be empty"


@pytest.mark.streaming
def test_invalid_segment_returns_error_code(streaming_validator: StreamingValidator) -> None:
    if os.getenv("FAST_MODE", "false") == "true":
        pytest.skip("Server error behavior not validated under FAST_MODE")

    streaming_validator.set_network_condition("normal")

    with pytest.raises(Exception):
        streaming_validator.get_segment(999)
