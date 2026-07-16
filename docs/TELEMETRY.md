# Telemetry and Monitoring

The telemetry subsystem exports the **complete mixer state** to external systems
**without modifying the `voctocore` core**. This is unique to Voctomix 2.0 and
not present in the original C3VOC system.

## Chain overview

`voctogui/lib/gui_state_exporter.py` collects state from the live `voctogui`
widget tree every second and publishes it through one of two paths depending on
the deployment mode:

```
voctogui (GuiStateExporter, 1 s timer)
   │
<<<<<<< HEAD
   ├─ native mode ─► registros/gui_state.json     (JSON Lines, one object/sample)
=======
   ├─ native mode ─► sessions/gui_state.json      (latest GUI-state snapshot)
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
   │
   └─ docker mode ─► HTTP POST :8080 ─► telemetry service ─► RabbitMQ AMQP :5672
                                                                  │
                                                  external consumers (dashboards,
                                                  alerting, recording services…)
```

<<<<<<< HEAD
- **Native deployments**: appends JSON records to `registros/gui_state.json`
  (one object per sampling instant), a persistent log for post-event analysis.
=======
- **Native deployments**: writes the latest GUI-state snapshot to
  `sessions/gui_state.json`. The telemetry service can read this file and append
  periodic `STATE` and change-driven `CHANGE` events to session JSONL logs when
  `SAVE_LOGS=true`.
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30
- **Docker deployments**: HTTP-POSTs the same JSON to the telemetry container on
  port 8080, which forwards it to a RabbitMQ AMQP exchange.

## Event types

| Event | Trigger | Purpose |
|---|---|---|
| `CHANGE` | Immediately on any state transition (source switch, mode change, blanker/overlay toggle) | Sub-second reaction latency for consumers |
| `STATE` | Periodic heartbeat (every 5 s) | Detect stale connections; reconstruct state after reconnection |

Separating change-driven from periodic events decouples monitoring freshness
from polling rate. The AMQP binding model lets any number of subscribers consume
events without touching the application.

## RabbitMQ

| Endpoint | Port | Use |
|---|---|---|
| AMQP | 5672 | Message broker (publish/subscribe) |
| Management UI | 15672 | Web dashboard (queues, throughput) |

The two-queue pattern (`CHANGE` / `STATE`) is visible in the management UI
during a session.

## JSON schema

A full snapshot published each second. Example:

```json
{
  "last_update": "2026-04-22 14:35:01",
  "gui_ip": "192.168.1.10",
  "preview": { "channel_a": "cam1", "channel_b": "cam2" },
  "mode": "live",
  "composite": {
    "name": "full_screen",
    "fullscreen": true, "side_by_side": false, "pip": false, "lecture": false
  },
  "mirror": false,
  "insertion": {
    "overlay": false, "auto_off": true,
    "overlay_selected": "logo_event.png",
    "text1_active": true, "text1_value": "Speaker Name",
    "text2_active": false, "text2_value": ""
  },
  "audio": {
    "cam1_db": -18.5, "cam2_db": -42.0,
    "cam3_db": null, "cam4_db": null,
    "break_db": null, "intro_db": null
  }
}
```

| Field | Meaning |
|---|---|
| `last_update` | Sampling timestamp |
| `gui_ip` | Operator host address |
| `preview.channel_a/b` | Sources assigned to channels A/B |
| `mode` | Stream blanker state (`live` / `pause` / `nostream`) |
| `composite.*` | Active composite mode flags |
| `insertion.*` | Overlay/titling state |
| `audio.*_db` | Per-source audio level in dB (`null` if inactive) |

## Access

<<<<<<< HEAD
- **Docker / network mode**: `http://localhost:8080/gui_state`
- **Native mode**: `registros/gui_state.json`
=======
- **Docker / network mode**: `POST /gui_state` on port 8080 receives GUI-state
  snapshots from `voctogui`.
- **Native mode**: `sessions/gui_state.json` contains the latest local GUI-state
  snapshot.
>>>>>>> 920adf625f85240b9410c616f7c7c875f625df30

## Future integrations (roadmap)

The JSON events feeding RabbitMQ are a natural integration point for a
Prometheus exporter (CPU/RAM/bandwidth/per-source status → Grafana dashboards)
and for a speech-to-text module publishing transcribed text as overlay commands.
