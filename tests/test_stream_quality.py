import asyncio

import pytest


@pytest.mark.streaming
@pytest.mark.asyncio  # Added decorator
class TestStreamQuality:
    async def test_stream_quality_degradation(self, streaming_validator):  # async def
        result = await streaming_validator.set_network_condition("normal")  # await
        await asyncio.sleep(0.5)  # await asyncio.sleep
        status = await streaming_validator.fetch_health_metric("status")  # await