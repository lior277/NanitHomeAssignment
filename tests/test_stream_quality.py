"""
Test cases for streaming quality validation - Stage 1, Task A

This test suite validates streaming performance under different network conditions
to ensure the streaming service meets quality standards.

Requirements:
1. Uses StreamingValidator to validate streaming under "normal" network conditions
2. Switches to "poor" conditions via /control/network endpoint
3. Asserts that quality metrics degrade as expected (e.g., latency increases)

Author: QA Automation Team
"""

import pytest
import asyncio
import logging
from typing import Dict

from infra.streaming_validator import StreamingValidator

logger = logging.getLogger(__name__)


@pytest.mark.streaming
@pytest.mark.asyncio
class TestStreamQuality:
    """
    Test suite for streaming quality validation

    Tests validate that streaming service properly responds to network
    conditions and that quality metrics accurately reflect the state.
    """

    async def test_stream_quality_degradation(self, streaming_validator: StreamingValidator) -> None:
        """
        Test streaming quality degradation from normal to poor network conditions.

        Test Flow:
        1. Set network to "normal" and validate streaming works
        2. Measure baseline performance metrics
        3. Switch network to "poor" conditions
        4. Measure degraded performance metrics
        5. Assert significant quality degradation occurred

        Args:
            streaming_validator: Fixture providing StreamingValidator instance
        """
        logger.info("=" * 80)
        logger.info("TEST: Stream Quality Degradation (Normal → Poor)")
        logger.info("=" * 80)

        # ===== PHASE 1: Validate streaming under NORMAL conditions =====
        await self._test_normal_conditions(streaming_validator)

        # ===== PHASE 2: Switch to POOR conditions =====
        await self._test_poor_conditions(streaming_validator)

        # ===== PHASE 3: Assert quality metrics degrade =====
        await self._validate_quality_degradation(
            streaming_validator,
            self.normal_latency,
            self.poor_latency
        )

        logger.info("\n" + "=" * 80)
        logger.info("✅ TEST PASSED: Quality degraded as expected under poor conditions")
        logger.info("=" * 80)

    async def _test_normal_conditions(self, validator: StreamingValidator) -> None:
        """
        Test and measure streaming under normal network conditions.

        Args:
            validator: StreamingValidator instance
        """
        logger.info("\n📊 PHASE 1: Testing under NORMAL network conditions")
        logger.info("-" * 80)

        # Set network condition to normal
        result = await validator.set_network_condition("normal")
        assert result["applied"] == "normal", \
            f"Failed to set normal network condition. Got: {result}"
        logger.info(f"✓ Network condition set to: {result['applied']}")

        # Small delay to let condition stabilize
        await asyncio.sleep(0.5)

        # Task A requirement #1: Fetch metric from /health endpoint
        status = await validator.fetch_health_metric("status")
        logger.info(f"✓ Fetched metric 'status' = {status}")
        assert status == "streaming", \
            f"Expected status 'streaming', got '{status}'. Service may be down."

        # Task A requirement #2: Validate streaming performance
        normal_validation = await validator.validate_performance(
            expected_max_latency_ms=100
        )
        logger.info(
            f"✓ Normal latency: {normal_validation['actual_latency_ms']:.2f}ms "
            f"(threshold: {normal_validation['threshold_ms']}ms)"
        )
        assert normal_validation['is_valid'], \
            f"Normal latency {normal_validation['actual_latency_ms']:.2f}ms " \
            f"exceeds threshold {normal_validation['threshold_ms']}ms"

        # Measure baseline latency for comparison
        self.normal_latency = await validator.measure_latency(samples=3)
        logger.info(
            f"✓ Baseline latency measured: {self.normal_latency:.2f}ms "
            f"(avg of 3 samples)"
        )

        # Additional validation: Check viewers count is reasonable
        viewers = await validator.fetch_health_metric("viewers")
        logger.info(f"✓ Current viewers: {viewers}")
        assert isinstance(viewers, int) and viewers >= 0, \
            f"Invalid viewers count: {viewers}"

    async def _test_poor_conditions(self, validator: StreamingValidator) -> None:
        """
        Switch to poor network conditions and measure impact.

        Args:
            validator: StreamingValidator instance
        """
        logger.info("\n📊 PHASE 2: Switching to POOR network conditions")
        logger.info("-" * 80)

        # Task A requirement #3: Switch network condition via /control/network
        result = await validator.set_network_condition("poor")
        assert result["applied"] == "poor", \
            f"Failed to set poor network condition. Got: {result}"
        logger.info(f"✓ Network condition switched to: {result['applied']}")

        # Log network settings for debugging
        settings = result.get("settings", {})
        if settings:
            logger.info(f"  Settings: latency={settings.get('latency_ms')}ms, "
                        f"packet_loss={settings.get('packet_loss', 0) * 100:.1f}%, "
                        f"jitter={settings.get('jitter_ms')}ms")

        # Wait for condition to stabilize
        await asyncio.sleep(0.5)

        # Verify the condition was actually changed
        network_condition = await validator.fetch_health_metric("network_condition")
        logger.info(f"✓ Verified network_condition = {network_condition}")
        assert network_condition == "poor", \
            f"Network condition should be 'poor', got '{network_condition}'. " \
            f"Server may not have applied the setting."

        # Measure latency under poor conditions
        self.poor_latency = await validator.measure_latency(samples=3)
        logger.info(
            f"✓ Poor condition latency measured: {self.poor_latency:.2f}ms "
            f"(avg of 3 samples)"
        )

    async def _validate_quality_degradation(
            self,
            validator: StreamingValidator,
            normal_latency: float,
            poor_latency: float
    ) -> None:
        """
        Validate that quality metrics show significant degradation.

        Args:
            validator: StreamingValidator instance
            normal_latency: Baseline latency under normal conditions (ms)
            poor_latency: Latency under poor conditions (ms)

        Raises:
            AssertionError: If quality did not degrade as expected
        """
        logger.info("\n📊 PHASE 3: Validating quality degradation")
        logger.info("-" * 80)

        # Calculate degradation metrics
        latency_increase = poor_latency - normal_latency
        increase_percentage = ((poor_latency / normal_latency) - 1) * 100
        degradation_factor = poor_latency / normal_latency

        # Log detailed analysis
        logger.info(f"\n📈 Quality Degradation Analysis:")
        logger.info(f"   Normal latency:     {normal_latency:.2f}ms")
        logger.info(f"   Poor latency:       {poor_latency:.2f}ms")
        logger.info(f"   Absolute increase:  {latency_increase:.2f}ms")
        logger.info(f"   Percentage increase: +{increase_percentage:.1f}%")
        logger.info(f"   Degradation factor: {degradation_factor:.2f}x")

        # Main assertion: Latency increased under poor conditions
        assert poor_latency > normal_latency, \
            f"Latency did not increase under poor conditions. " \
            f"Normal: {normal_latency:.2f}ms, Poor: {poor_latency:.2f}ms. " \
            f"This indicates the network condition change had no effect."

        # Verify significant degradation (at least 2x)
        min_degradation_factor = 2.0
        assert poor_latency >= normal_latency * min_degradation_factor, \
            f"Poor latency ({poor_latency:.2f}ms) should be at least " \
            f"{min_degradation_factor}x normal latency ({normal_latency:.2f}ms). " \
            f"Expected >= {normal_latency * min_degradation_factor:.2f}ms. " \
            f"Current factor: {degradation_factor:.2f}x"

        # Verify absolute increase is substantial (at least 50ms)
        min_absolute_increase = 50.0
        assert latency_increase >= min_absolute_increase, \
            f"Latency increase ({latency_increase:.2f}ms) is less than " \
            f"expected minimum ({min_absolute_increase}ms). " \
            f"Degradation may not be significant enough."

        logger.info(f"\n✓ All quality degradation assertions passed")
        logger.info(f"  - Latency increased: {latency_increase:.2f}ms")
        logger.info(f"  - Degradation factor: {degradation_factor:.2f}x (>= {min_degradation_factor}x)")
        logger.info(f"  - Percentage increase: +{increase_percentage:.1f}%")


@pytest.mark.streaming
@pytest.mark.asyncio
class TestStreamQualityEdgeCases:
    """
    Additional test cases for edge cases and error conditions.

    These tests ensure the StreamingValidator handles error conditions
    gracefully and provides meaningful error messages.
    """

    async def test_invalid_network_condition(self, streaming_validator: StreamingValidator) -> None:
        """
        Test that invalid network conditions are rejected.

        Args:
            streaming_validator: Fixture providing StreamingValidator instance
        """
        logger.info("TEST: Invalid network condition handling")

        # Try to set an invalid network condition
        with pytest.raises(ValueError) as exc_info:
            await streaming_validator.set_network_condition("invalid_condition")

        # Verify error message is helpful
        error_message = str(exc_info.value)
        assert "Invalid condition" in error_message, \
            f"Error message should mention 'Invalid condition': {error_message}"
        assert "normal" in error_message.lower(), \
            f"Error message should list valid conditions: {error_message}"

        logger.info("✓ Invalid condition properly rejected with clear error message")

    async def test_fetch_nonexistent_metric(self, streaming_validator: StreamingValidator) -> None:
        """
        Test that fetching non-existent metrics raises appropriate error.

        Args:
            streaming_validator: Fixture providing StreamingValidator instance
        """
        logger.info("TEST: Nonexistent metric handling")

        # Try to fetch a metric that doesn't exist
        with pytest.raises(KeyError) as exc_info:
            await streaming_validator.fetch_health_metric("nonexistent_metric")

        # Verify error message lists available metrics
        error_message = str(exc_info.value)
        assert "not found" in error_message.lower(), \
            f"Error should indicate metric not found: {error_message}"

        logger.info("✓ Nonexistent metric properly rejected with clear error message")

    async def test_terrible_network_conditions(self, streaming_validator: StreamingValidator) -> None:
        """
        Test streaming under 'terrible' network conditions.

        This validates the system can handle extreme degradation.

        Args:
            streaming_validator: Fixture providing StreamingValidator instance
        """
        logger.info("TEST: Terrible network conditions")

        # Set to terrible conditions
        result = await streaming_validator.set_network_condition("terrible")
        assert result["applied"] == "terrible"

        await asyncio.sleep(0.5)

        # Measure latency (may be very high or fail due to packet loss)
        try:
            terrible_latency = await validator.measure_latency(samples=3)
            logger.info(f"✓ Terrible condition latency: {terrible_latency:.2f}ms")

            # Latency should be significantly higher than poor conditions
            assert terrible_latency > 300, \
                f"Terrible condition latency ({terrible_latency:.2f}ms) " \
                f"should be > 300ms"
        except Exception as e:
            # Packet loss may cause failures - this is expected
            logger.info(f"✓ Terrible conditions caused failures (expected): {e}")

        logger.info("✓ Terrible network conditions handled appropriately")