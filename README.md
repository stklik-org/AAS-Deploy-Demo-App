# demo-app

A lightweight demonstration application comprising:

- A **Flask web server** that renders a status page displaying the container hostname and current UTC time.  The accent colour is configurable, allowing multiple instances to be visually distinguished at a glance.
- A **background MQTT publisher** that emits random floating-point values (0–100) to a configurable topic at a configurable interval, suitable for ingestion by Telegraf → InfluxDB pipelines.

---

## Configuration reference

All parameters follow the resolution priority:

```
CLI argument  >  Environment variable  >  Hard-coded default
```

| CLI flag            | Environment variable   | Default         | Description                            |
|---------------------|------------------------|-----------------|----------------------------------------|
| `--web-host`        | `DEMO_WEB_HOST`        | `0.0.0.0`       | Flask bind address                     |
| `--web-port`        | `DEMO_WEB_PORT`        | `5000`          | Flask TCP port                         |
| `--color`           | `DEMO_COLOR`           | `#2563eb`       | Accent colour (hex or basic name)      |
| `--mqtt-host`       | `DEMO_MQTT_HOST`       | `localhost`     | MQTT broker hostname / IP              |
| `--mqtt-port`       | `DEMO_MQTT_PORT`       | `1883`          | MQTT broker port                       |
| `--mqtt-user`       | `DEMO_MQTT_USER`       | *(empty)*       | MQTT username                          |
| `--mqtt-pass`       | `DEMO_MQTT_PASS`       | *(empty)*       | MQTT password                          |
| `--mqtt-topic`      | `DEMO_MQTT_TOPIC`      | `demo/values`   | Base topic; app publishes to `<base-topic>/<hostname>` |
| `--mqtt-interval`   | `DEMO_MQTT_INTERVAL`   | `5`             | Publish interval in seconds            |

---

## Running locally (without Docker)

```bash
pip install -r requirements.txt

python app.py \
  --color "#dc2626" \
  --mqtt-host 192.168.1.100 \
  --mqtt-topic lab/sensors/temperature \
  --mqtt-interval 2
```

---

## Running in Docker

### Build

```bash
docker build -t demo-app .
```

### GitHub Container Registry (automatic)

This repository includes a workflow at
`.github/workflows/docker-publish.yml` that builds and pushes the image to:

`ghcr.io/stklik-org/aas-deploy-demo-app`

It runs on:
- push to `main` (publishes `:latest`, `:main`, `:sha-...`)
- version tags like `v1.2.3` (publishes tag-based image tags)

Example pull/run:

```bash
docker pull ghcr.io/stklik-org/aas-deploy-demo-app:latest
docker run --rm -p 5000:5000 ghcr.io/stklik-org/aas-deploy-demo-app:latest
```

### Single container

```bash
docker run --rm \
  -p 5000:5000 \
  -e DEMO_COLOR="#dc2626" \
  -e DEMO_MQTT_HOST=192.168.1.100 \
  -e DEMO_MQTT_TOPIC=lab/sensors/temperature \
  ghcr.io/stklik-org/aas-deploy-demo-app:latest
```

CLI flags take precedence over environment variables, so the following overrides the colour regardless of `DEMO_COLOR`:

```bash
docker run --rm -p 5000:5000 -e DEMO_COLOR="#dc2626" ghcr.io/stklik-org/aas-deploy-demo-app:latest --color "#16a34a"
```

### Multiple instances via Docker Compose

```bash
# Start two instances (blue on :5001, green on :5002) plus a Mosquitto broker
docker compose up --build
```

When app and broker run in separate containers on the same Compose network,
set `DEMO_MQTT_HOST` to the broker service name (typically `mqtt`), not `localhost`.

---

## Telegraf integration example

```toml
[[inputs.mqtt_consumer]]
  servers = ["tcp://localhost:1883"]
  topics  = ["demo/+/values"]
  data_format = "value"
  data_type   = "float"
```

---

## Endpoints

| Path      | Description                              |
|-----------|------------------------------------------|
| `GET /`   | Status page (hostname + time + config)   |
| `GET /health` | JSON health-check: `{"status":"ok"}` |

---

## Install via pip (from Git repo)

You can install directly from GitHub:

```bash
pip install "git+https://github.com/stklik-org/AAS-Deploy-Demo-App.git"
```

Then run:

```bash
demo-app
```

For reproducible installs, pin to a tag or commit:

```bash
pip install "git+https://github.com/stklik-org/AAS-Deploy-Demo-App.git@v0.1.0"
pip install "git+https://github.com/stklik-org/AAS-Deploy-Demo-App.git@<commit-sha>"
```
