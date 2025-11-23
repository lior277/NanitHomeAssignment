"""Small CLI example to exercise the StreamingValidator."""

from __future__ import annotations

import logging

import requests

from config.config import StreamingConfig
from infra.streaming.streaming_validator import StreamingValidator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)


def main() -> None:
    """Run a simple manual check against the streaming backend."""
    config = StreamingConfig()
    validator = StreamingValidator(config=config)

    try:
        validator.set_network_condition("normal")
        latency = validator.get_latency_ms()
        manifest = validator.get_manifest()
    except requests.RequestException as exc:
        logging.getLogger(__name__).error("Failed to query streaming backend: %s", exc)
        return

    print("Health latency_ms:", latency)
    print("Manifest starts with:", manifest.splitlines()[0])


if __name__ == "__main__":
    main()
