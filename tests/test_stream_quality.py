from __future__ import annotations
import pytest

from infra.streaming.streaming_validator import StreamingValidator


@pytest.mark.streaming
def test_stream_latency_degrades_from_normal_to_poor(
    streaming_validator: StreamingValidator,
) -> None:
    streaming_validator.set_network_condition("normal")
    normal_latency = streaming_validator.get_latency_ms()

    streaming_validator.set_network_condition("poor")
    poor_latency = streaming_validator.get_latency_ms()

    assert poor_latency > normal_latency


@pytest.mark.streaming
@pytest.mark.parametrize("condition", ["normal", "poor", "terrible"])
def test_manifest_available_under_all_conditions(
    streaming_validator: StreamingValidator,
    condition: str,
) -> None:
    streaming_validator.set_network_condition(condition)
    manifest = streaming_validator.get_manifest()
    assert "#EXTM3U" in manifest


@pytest.mark.streaming
def test_segments_reachable_under_normal_conditions(
    streaming_validator: StreamingValidator,
) -> None:
    streaming_validator.set_network_condition("normal")

    for index in range(1, 6):
        data = streaming_validator.get_segment(index)
        assert data, f"Segment {index} should not be empty"


@pytest.mark.streaming
def test_invalid_segment_returns_error(streaming_validator: StreamingValidator) -> None:

    streaming_validator.set_network_condition("normal")

    with pytest.raises(Exception):
        streaming_validator.get_segment(999)
