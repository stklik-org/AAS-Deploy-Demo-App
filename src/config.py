import argparse
import os


def _resolve(cli_val, env_key: str, default):
    """
    Resolve a configuration value following the priority chain:
      CLI argument  >  Environment variable  >  Default value

    Parameters
    ----------
    cli_val : any
        Value supplied via CLI (``None`` if the flag was not provided).
    env_key : str
        Name of the corresponding environment variable.
    default : any
        Fallback value when neither CLI nor environment provides a value.

    Returns
    -------
    any
        The resolved configuration value.
    """
    if cli_val is not None:
        return cli_val
    env_val = os.environ.get(env_key)
    if env_val is not None:
        return env_val
    return default


def _fallback_if_blank(value, default):
    """Return default when value is None or blank string."""
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return value


def _safe_int(value, default: int) -> int:
    """Convert value to int, returning default on invalid input."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_config(args: argparse.Namespace) -> dict:
    """Construct the application configuration dictionary."""
    mqtt_host = _fallback_if_blank(_resolve(args.mqtt_host, "DEMO_MQTT_HOST", "localhost"), "localhost")
    mqtt_port = _safe_int(_fallback_if_blank(_resolve(args.mqtt_port, "DEMO_MQTT_PORT", 1883), 1883), 1883)

    return {
        "web_host":      _resolve(args.web_host,      "DEMO_WEB_HOST",      "0.0.0.0"),
        "web_port":      int(_resolve(args.web_port,  "DEMO_WEB_PORT",      5000)),
        "color":         _resolve(args.color,         "DEMO_COLOR",         "#2563eb"),
        "custom_label":  _resolve(args.custom_label,  "DEMO_CUSTOM_LABEL",  ""),
        "mqtt_host":     mqtt_host,
        "mqtt_port":     mqtt_port,
        "mqtt_user":     _resolve(args.mqtt_user,     "DEMO_MQTT_USER",     ""),
        "mqtt_pass":     _resolve(args.mqtt_pass,     "DEMO_MQTT_PASS",     ""),
        "mqtt_topic":    _resolve(args.mqtt_topic,    "DEMO_MQTT_TOPIC",    "demo/values"),
        "mqtt_interval": float(_resolve(args.mqtt_interval, "DEMO_MQTT_INTERVAL", 5)),
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Demo application: Flask status page + MQTT random-value publisher.\n"
            "Priority for each setting:  CLI argument > Environment variable > Default."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Web server
    web = p.add_argument_group("Web server")
    web.add_argument("--web-host",  default=None, metavar="HOST",
                     help="Bind address for Flask  [env: DEMO_WEB_HOST]  (default: 0.0.0.0)")
    web.add_argument("--web-port",  default=None, metavar="PORT", type=int,
                     help="TCP port for Flask  [env: DEMO_WEB_PORT]  (default: 5000)")
    web.add_argument("--color",     default=None, metavar="CSS_COLOR",
                     help="Accent colour (hex or basic name, e.g. red/blue)  [env: DEMO_COLOR]  (default: #2563eb)")
    web.add_argument("--custom-label", default=None, metavar="LABEL",
                     help="Custom label displayed below hostname  [env: DEMO_CUSTOM_LABEL]  (default: none)")

    # MQTT
    mq = p.add_argument_group("MQTT")
    mq.add_argument("--mqtt-host",     default=None, metavar="HOST",
                    help="MQTT broker hostname / IP  [env: DEMO_MQTT_HOST]  (default: localhost)")
    mq.add_argument("--mqtt-port",     default=None, metavar="PORT", type=int,
                    help="MQTT broker port  [env: DEMO_MQTT_PORT]  (default: 1883)")
    mq.add_argument("--mqtt-user",     default=None, metavar="USER",
                    help="MQTT username  [env: DEMO_MQTT_USER]  (default: none)")
    mq.add_argument("--mqtt-pass",     default=None, metavar="PASS",
                    help="MQTT password  [env: DEMO_MQTT_PASS]  (default: none)")
    mq.add_argument("--mqtt-topic",    default=None, metavar="TOPIC",
                    help="Topic to publish to  [env: DEMO_MQTT_TOPIC]  (default: demo/values)")
    mq.add_argument("--mqtt-interval", default=None, metavar="SECONDS", type=float,
                    help="Publish interval in seconds  [env: DEMO_MQTT_INTERVAL]  (default: 5)")

    return p
