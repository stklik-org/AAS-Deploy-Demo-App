import logging
import random
import socket
import threading
import time

import paho.mqtt.client as mqtt

log = logging.getLogger("demo_app")


class MqttPublisher(threading.Thread):
    """
    Background daemon thread that maintains an MQTT connection and publishes
    a random floating-point value to the configured topic at a fixed interval.
    """

    def __init__(self, cfg: dict):
        super().__init__(name="mqtt-publisher", daemon=True)
        self.cfg = cfg
        self._client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"demo-{socket.gethostname()}",
        )

        if cfg["mqtt_user"]:
            self._client.username_pw_set(cfg["mqtt_user"], cfg["mqtt_pass"])

        self._client.on_connect    = self._on_connect
        self._client.on_disconnect = self._on_disconnect

    # ------------------------------------------------------------------
    # MQTT callbacks
    # ------------------------------------------------------------------

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if not reason_code.is_failure:
            log.info("MQTT connected to %s:%s", self.cfg["mqtt_host"], self.cfg["mqtt_port"])
        else:
            log.warning("MQTT connection failed: %s", reason_code)

    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties):
        if reason_code.is_failure:
            log.warning("MQTT unexpected disconnection (%s); will attempt reconnect", reason_code)

    def _connection_candidates(self) -> list[str]:
        """
        Return host candidates for Docker/local setups.
        - Use configured host first.
        - If host is localhost/127.0.0.1, also try common Docker targets.
        """
        configured = str(self.cfg["mqtt_host"]).strip() or "localhost"
        candidates = [configured]

        if configured in {"localhost", "127.0.0.1"}:
            for fallback in ("mqtt", "host.docker.internal"):
                if fallback not in candidates:
                    candidates.append(fallback)

        return candidates

    # ------------------------------------------------------------------
    # Thread entry point
    # ------------------------------------------------------------------

    def run(self):
        """Connect to the broker and enter the publish loop."""
        while True:
            connected = False
            for host in self._connection_candidates():
                try:
                    self._client.connect(
                        host,
                        self.cfg["mqtt_port"],
                        keepalive=60,
                    )
                    self.cfg["mqtt_host"] = host
                    connected = True
                    break
                except Exception as exc:
                    log.warning("MQTT connect failed to %s:%s (%s)", host, self.cfg["mqtt_port"], exc)

            if not connected:
                log.error("MQTT error: all connection attempts failed — retrying in 10 s")
                time.sleep(10)
                continue

            self._client.loop_start()
            try:
                self._publish_loop()
            except Exception as exc:
                log.error("MQTT error: %s — retrying in 10 s", exc)
                time.sleep(10)
            finally:
                self._client.loop_stop()
                self._client.disconnect()

    def _publish_loop(self):
        topic    = self.cfg["mqtt_topic"]
        interval = self.cfg["mqtt_interval"]

        while True:
            value = round(random.uniform(0.0, 100.0), 4)
            result = self._client.publish(topic, payload=str(value), qos=1)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                log.info("MQTT published %.4f  →  %s", value, topic)
            else:
                log.warning("MQTT publish failed (rc=%d)", result.rc)
            time.sleep(interval)
