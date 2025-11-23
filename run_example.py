"""Simple usage example of the streaming validator."""

import logging
from time import sleep
from infra.page_objects.http_client import HttpClient
from infra.streaming.streaming_validator import StreamingConfig
from config import StreamingConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def main():
    """Demonstrate streaming validator usage."""
    config = StreamingConfig()
    http_client = HttpClient(timeout=config.timeout)
    validator = StreamingConfig(http_client=http_client, config=config)

    try:
        # Test normal conditions
        print("\n=== Testing NORMAL conditions ===")
        validator.set_network_condition("normal")
        sleep(0.2)
        bitrate = validator.get_bitrate()
        print(f"Bitrate: {bitrate} kbps")

        # Test poor conditions
        print("\n=== Testing POOR conditions ===")
        validator.set_network_condition("poor")
        sleep(0.2)
        bitrate = validator.get_bitrate()
        print(f"Bitrate: {bitrate} kbps")

        # Test terrible conditions
        print("\n=== Testing TERRIBLE conditions ===")
        validator.set_network_condition("terrible")
        sleep(0.2)
        bitrate = validator.get_bitrate()
        print(f"Bitrate: {bitrate} kbps")

        print(" All tests completed!")

    except Exception as e:
        print(f" Error: {e}")
        print("Make sure the mock server is running:")
        print("  python mock_services/mock_streaming_server.py")
    finally:
        http_client.close()


if __name__ == "__main__":
    main()