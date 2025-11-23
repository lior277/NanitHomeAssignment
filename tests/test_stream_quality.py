"""Integration tests for streaming validator (requires mock server running)."""

import pytest
import time
from infra.http_client import HttpClient
from infra.streaming_validator import StreamingValidator
from config import StreamingConfig


@pytest.fixture
def config():
    """Create test configuration."""
    return StreamingConfig()


@pytest.fixture
def http_client(config):
    """Create HTTP client."""
    client = HttpClient(timeout=config.timeout)
    yield client
    client.close()


@pytest.fixture
def validator(http_client, config):
    """Create validator with dependency injection."""
    return StreamingValidator(http_client=http_client, config=config)


@pytest.fixture(autouse=True)
def reset_to_normal(validator):
    """Reset network condition to normal before each test."""
    try:
        validator.set_network_condition("normal")
        time.sleep(0.1)  # Allow condition to stabilize
    except Exception:
        pytest.skip("Mock server not available")
    yield


def test_validate_streaming_under_normal_conditions(validator):
    """Test streaming validation under normal network conditions."""
    # Arrange - Set normal conditions
    success = validator.set_network_condition("normal")
    assert success, "Failed to set normal network condition"
    time.sleep(0.1)

    # Act - Get metrics
    metrics = validator.get_health_metrics()
    bitrate = validator.get_bitrate()
    condition = validator.get_network_condition()

    # Assert
    assert metrics["status"] == "healthy"
    assert bitrate >= 2000, f"Normal bitrate should be >= 2000, got {bitrate}"
    assert condition == "normal"
    assert validator.validate_bitrate_in_range(2000, 3000)
    assert validator.validate_network_condition("normal")


def test_switch_to_poor_conditions_and_verify_degradation(validator):
    """Test switching to poor conditions and verify quality degrades."""
    # Arrange - Get baseline under normal conditions
    validator.set_network_condition("normal")
    time.sleep(0.1)
    normal_bitrate = validator.get_bitrate()

    # Act - Switch to poor conditions
    success = validator.set_network_condition("poor")
    assert success, "Failed to set poor network condition"
    time.sleep(0.1)

    # Get metrics under poor conditions
    poor_metrics = validator.get_health_metrics()
    poor_bitrate = validator.get_bitrate()
    poor_condition = validator.get_network_condition()

    # Assert - Quality should degrade
    assert poor_condition == "poor", f"Expected 'poor', got '{poor_condition}'"
    assert poor_bitrate < normal_bitrate, \
        f"Bitrate should decrease: normal={normal_bitrate}, poor={poor_bitrate}"
    assert poor_bitrate < 1500, f"Poor bitrate should be < 1500, got {poor_bitrate}"

    # Validate with appropriate thresholds for poor conditions
    assert validator.validate_bitrate_in_range(1000, 1500)
    assert validator.validate_network_condition("poor")


def test_quality_metrics_degrade_progressively(validator):
    """Test that quality metrics degrade as network conditions worsen."""
    # Collect bitrates for all conditions
    bitrates = {}
    conditions = ["normal", "poor", "terrible"]

    for condition in conditions:
        validator.set_network_condition(condition)
        time.sleep(0.1)
        bitrates[condition] = validator.get_bitrate()

    # Assert - Progressive degradation
    assert bitrates["normal"] > bitrates["poor"], \
        f"Normal bitrate ({bitrates['normal']}) should be > poor ({bitrates['poor']})"

    assert bitrates["poor"] > bitrates["terrible"], \
        f"Poor bitrate ({bitrates['poor']}) should be > terrible ({bitrates['terrible']})"

    # Verify actual values match expected ranges
    assert 2000 <= bitrates["normal"] <= 3000
    assert 1000 <= bitrates["poor"] <= 1500
    assert 400 <= bitrates["terrible"] <= 600


def test_switch_between_conditions_multiple_times(validator):
    """Test switching between different network conditions multiple times."""
    test_sequence = [
        ("normal", 2000, 3000),
        ("poor", 1000, 1500),
        ("terrible", 400, 600),
        ("normal", 2000, 3000),
        ("poor", 1000, 1500),
    ]

    for condition, min_bitrate, max_bitrate in test_sequence:
        # Set condition
        success = validator.set_network_condition(condition)
        assert success, f"Failed to set {condition} condition"
        time.sleep(0.1)

        # Verify condition
        current_condition = validator.get_network_condition()
        assert current_condition == condition, \
            f"Expected {condition}, got {current_condition}"

        # Verify bitrate is in expected range
        assert validator.validate_bitrate_in_range(min_bitrate, max_bitrate), \
            f"Bitrate validation failed for {condition} condition"


def test_latency_increases_with_poor_conditions(validator):
    """Test that latency increases as conditions worsen."""
    import time

    # Measure time under normal conditions
    validator.set_network_condition("normal")
    time.sleep(0.1)

    start = time.time()
    validator.get_health_metrics()
    normal_latency = time.time() - start

    # Measure time under poor conditions
    validator.set_network_condition("poor")
    time.sleep(0.1)

    start = time.time()
    validator.get_health_metrics()
    poor_latency = time.time() - start

    # Assert - Poor conditions should have higher latency
    assert poor_latency > normal_latency, \
        f"Poor latency ({poor_latency:.3f}s) should be > normal ({normal_latency:.3f}s)"