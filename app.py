"""Entry point. See src/ for module implementations."""
import logging
import socket

from flask import Flask

from src.config import build_config, build_parser
from src.mqtt_publisher import MqttPublisher
from src.web_server import create_flask_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
log = logging.getLogger("demo_app")


def _topic_with_hostname(base_topic: str, hostname: str) -> str:
    """Append hostname to configured base topic."""
    return f"{base_topic.rstrip('/')}/{hostname}"


def main():
    parser = build_parser()
    args = parser.parse_args()
    cfg = build_config(args)
    hostname = socket.gethostname()
    cfg["mqtt_topic"] = _topic_with_hostname(cfg["mqtt_topic"], hostname)
    log.info("Starting demo application with configuration: %s", cfg)
    publisher = MqttPublisher(cfg)
    publisher.start()
    log.info("MQTT publisher thread started")
    app = create_flask_app(cfg)
    log.info("Flask server starting on %s:%d", cfg["web_host"], cfg["web_port"])
    app.run(host=cfg["web_host"], port=cfg["web_port"], debug=False, use_reloader=True)


if __name__ == "__main__":
    main()
