import socket
import time

from flask import Flask, render_template_string

_BASIC_COLOR_MAP = {
    "aliceblue": "#f0f8ff",
    "aqua": "#00ffff",
    "aquamarine": "#7fffd4",
    "beige": "#f5f5dc",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "white": "#ffffff",
    "silver": "#c0c0c0",
    "maroon": "#800000",
    "navy": "#000080",
    "olive": "#808000",
    "teal": "#008080",
    "lime": "#00ff00",
    "red": "#ff0000",
    "green": "#008000",
    "blue": "#0000ff",
    "yellow": "#ffff00",
    "orange": "#ffa500",
    "purple": "#800080",
    "violet": "#ee82ee",
    "indigo": "#4b0082",
    "pink": "#ffc0cb",
    "coral": "#ff7f50",
    "salmon": "#fa8072",
    "gold": "#ffd700",
    "khaki": "#f0e68c",
    "turquoise": "#40e0d0",
    "lavender": "#e6e6fa",
    "crimson": "#dc143c",
    "tomato": "#ff6347",
    "chocolate": "#d2691e",
    "brown": "#a52a2a",
    "tan": "#d2b48c",
    "wheat": "#f5deb3",
    "gray": "#808080",
    "grey": "#808080",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "darkgray": "#a9a9a9",
    "darkgrey": "#a9a9a9",
    "slategray": "#708090",
    "slategrey": "#708090",
    "lightblue": "#add8e6",
    "lightgreen": "#90ee90",
    "darkblue": "#00008b",
    "darkgreen": "#006400",
    "darkred": "#8b0000",
    "cyan": "#00ffff",
    "magenta": "#ff00ff",
}


def _normalize_color_to_hex(color: str) -> str:
    """Normalize a color string into a 6-digit lowercase hex color."""
    value = color.strip().lower()
    if value in _BASIC_COLOR_MAP:
        return _BASIC_COLOR_MAP[value]

    if value.startswith("#"):
        value = value[1:]

    if len(value) == 3 and all(c in "0123456789abcdef" for c in value):
        value = "".join(c * 2 for c in value)

    if len(value) == 6 and all(c in "0123456789abcdef" for c in value):
        return f"#{value}"

    raise ValueError(f"Unsupported color value '{color}'. Use hex or a basic color name.")


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB values to hex color string."""
    return f"#{r:02x}{g:02x}{b:02x}"


def _darken_color(hex_color: str, factor: float = 0.7) -> str:
    """Darken a hex color by multiplying RGB values by factor."""
    r, g, b = _hex_to_rgb(hex_color)
    r = int(r * factor)
    g = int(g * factor)
    b = int(b * factor)
    return _rgb_to_hex(r, g, b)


def _lighten_color(hex_color: str, factor: float = 0.3) -> str:
    """Lighten a hex color by adding factor to RGB values."""
    r, g, b = _hex_to_rgb(hex_color)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return _rgb_to_hex(r, g, b)


def _is_light_color(hex_color: str) -> bool:
    """Return True when color luminance indicates a light color."""
    r, g, b = _hex_to_rgb(hex_color)
    luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
    return luminance > 0.6

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="refresh" content="5" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Demo Instance — {{ hostname }}</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --accent: {{ color }};
      --accent-light: {{ accent_glow }};
      --accent-dark: {{ color_dark }};
      --accent-darker: {{ color_darker }};
      --text-primary: {{ text_primary }};
      --text-secondary: {{ text_secondary }};
      --text-muted: {{ text_muted }};
      --border-soft: {{ border_soft }};
      --badge-text: {{ badge_text }};
      --title-color: {{ title_color }};
    }

    body {
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: linear-gradient(135deg, var(--accent-darker) 0%, var(--accent-dark) 100%);
      color: var(--text-primary);
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .card {
      background: var(--accent-dark);
      border: 1px solid var(--accent);
      border-top: 4px solid var(--accent);
      border-radius: 12px;
      padding: 2.5rem 3rem;
      width: min(480px, 90vw);
      box-shadow: 0 0 40px var(--accent-light);
    }

    .badge {
      display: inline-block;
      background: var(--accent-light);
      color: var(--badge-text);
      border: 1px solid var(--accent);
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 0.25rem 0.6rem;
      margin-bottom: 1.25rem;
    }

    h1 {
      font-size: 1.6rem;
      font-weight: 700;
      color: var(--title-color);
      margin-bottom: 0.25rem;
      word-break: break-all;
    }

    .label {
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-top: 1.5rem;
      margin-bottom: 0.25rem;
    }

    .value {
      font-size: 1.1rem;
      color: var(--text-secondary);
      font-variant-numeric: tabular-nums;
    }

    .divider {
      border: none;
      border-top: 1px solid var(--border-soft);
      margin: 1.5rem 0;
    }

    .meta {
      font-size: 0.78rem;
      color: var(--text-muted);
      margin-top: 1.5rem;
    }

    .dot {
      display: inline-block;
      width: 8px; height: 8px;
      background: var(--accent);
      border-radius: 50%;
      margin-right: 6px;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50%       { opacity: 0.3; }
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="badge"><span class="dot"></span>Live</div>

    <div class="label">Hostname</div>
    <h1>{{ hostname }}</h1>

    <hr class="divider" />

    <div class="label">Current Time (UTC)</div>
    <div class="value">{{ current_time }}</div>

    <div class="label">MQTT Topic</div>
    <div class="value">{{ mqtt_topic }}</div>

    <div class="label">Publish Interval</div>
    <div class="value">{{ mqtt_interval }} s</div>

    <p class="meta">Page auto-refreshes every 5 s.</p>
  </div>
</body>
</html>
"""


def create_flask_app(cfg: dict) -> Flask:
    """Instantiate and configure the Flask application."""
    app = Flask(__name__)
    hostname = socket.gethostname()
    accent_color = _normalize_color_to_hex(cfg["color"])
    is_light = _is_light_color(accent_color)
    accent_dark = _darken_color(accent_color, factor=0.35 if is_light else 0.5)
    accent_darker = _darken_color(accent_color, factor=0.18 if is_light else 0.2)
    title_color = _darken_color(accent_color, factor=0.45) if is_light else _lighten_color(accent_color, factor=0.2)

    @app.route("/")
    def index():
        rendered = render_template_string(
            HTML_TEMPLATE,
            hostname=hostname,
            current_time=time.strftime("%Y-%m-%d  %H:%M:%S", time.gmtime()),
            color=accent_color,
            accent_glow=f"{accent_color}33",
            color_dark=accent_dark,
            color_darker=accent_darker,
            text_primary="#f8fafc",
            text_secondary="#e2e8f0",
            text_muted="#94a3b8",
            border_soft="#334155",
            badge_text="#0f172a" if is_light else "#e2e8f0",
            title_color=title_color,
            mqtt_topic=cfg["mqtt_topic"],
            mqtt_interval=cfg["mqtt_interval"],
        )
        return rendered

    @app.route("/health")
    def health():
        return {"status": "ok", "hostname": hostname}, 200

    return app
