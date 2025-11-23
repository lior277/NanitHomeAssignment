# tests/test_stream_quality.py

import pytest
from infra.streaming_validator import StreamingValidator


@pytest.fixture(scope="module")
def streaming_validator() -> StreamingValidator:
    return StreamingValidator("http://localhost:8082")


def test_stream_quality_degrades_under_poor_network(streaming_validator: StreamingValidator):
    v = streaming_validator

    # ---- Normal network baseline ------------------------------------------------
    v.set_network_condition("normal")
    normal_latency = v.get_latency_ms()
    manifest_normal = v.get_manifest()
    assert "#EXTM3U" in manifest_normal

    # ---- Poor network -----------------------------------------------------------
    v.set_network_condition("poor")
    poor_latency = v.get_latency_ms()
    manifest_poor = v.get_manifest()
    assert "#EXTM3U" in manifest_poor

    # ---- Assert performance degradation ----------------------------------------
    assert poor_latency > normal_latency, (
        f"Expected latency increase: normal={normal_latency}, poor={poor_latency}"
    )
