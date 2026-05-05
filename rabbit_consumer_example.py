#!/usr/bin/env python3
"""
Example RabbitMQ consumer for the Voctomix event exchange.
Prints every state change and periodic heartbeat published by the telemetry service.

Usage:
    python3 rabbit_consumer_example.py

Override host or credentials via environment variables:
    RABBITMQ_HOST=<host_ip> python3 rabbit_consumer_example.py
"""

import json
import os
import sys
from datetime import datetime

try:
    import pika
except ImportError:
    print("pika is not installed. Run: pip3 install pika")
    sys.exit(1)

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "voctomix")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "voctomix123")
RABBITMQ_EXCHANGE = "voctomix_events"


def on_message(channel, method, properties, body):
    try:
        data = json.loads(body.decode())
    except Exception:
        print(f"[RAW] {body}")
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    event_type = data.get("type", "?")
    output = data.get("output", {})
    mode = data.get("mode", "?")
    composite = data.get("composite", {}).get("name", "?")
    sources = data.get("sources", {})

    active_sources = [k for k, v in sources.items() if v]
    health = data.get("system_health", {})

    print(f"\n[{timestamp}] -- EVENT: {event_type.upper()} ------------------")
    print(f"  Program   : A={output.get('channel_a', '?')}  B={output.get('channel_b', '?')}")
    print(f"  Mode      : {mode}   Composite: {composite}")
    print(f"  Sources ON: {active_sources if active_sources else 'none'}")
    print(f"  CPU: {health.get('cpu_usage_percent', '?')}%  "
          f"RAM: {health.get('ram_usage_percent', '?')}%  "
          f"Session: {health.get('session_duration', '?')}")


def main():
    print(f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}...")
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=10
    )
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare the exchange (idempotent: safe to call even if it already exists)
    channel.exchange_declare(
        exchange=RABBITMQ_EXCHANGE,
        exchange_type='fanout',
        durable=True
    )

    # Exclusive temporary queue: automatically deleted when this consumer disconnects
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange=RABBITMQ_EXCHANGE, queue=queue_name)

    print(f"Subscribed to exchange '{RABBITMQ_EXCHANGE}'. Waiting for events...")
    print("   (Press Ctrl+C to quit)\n")

    channel.basic_consume(
        queue=queue_name,
        on_message_callback=on_message,
        auto_ack=True
    )

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nConsumer disconnected.")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == '__main__':
    main()
