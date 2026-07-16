"""Reusable helper health payload fixtures for IH dashboard tests.

These produce the raw GET /health JSON shape that the collector helper
emits. Each fixture factory accepts ``**overrides`` to mutate specific
fields for a given test scenario.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


NOW = datetime.now(timezone.utc)


def chat_healthy_payload(**overrides: Any) -> dict[str, Any]:
    """Payload with chat healthy (recent message, writes OK, retention current)."""
    base: dict[str, Any] = {
        "type": "idlehacking_collector_health",
        "schema_version": 1,
        "updated_at": (NOW - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "ok",
        "chat": {
            "status": "ok",
            "last_message_at": (NOW - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "messages_seen": 142,
            "writes_ok": 4555,
            "writes_failed": 4554,
        },
        "market": {
            "status": "down",
            "last_capture_at": (NOW - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "commodities": None,
            "books": None,
        },
        "volume": {"status": "ok", "last_change_at": (NOW - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"), "changes_seen": 12},
        "errors": [],
        "storage_retention": {
            "chat": {
                "updated_at": (NOW - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "idlehacking_kb",
                "collection_status": "success",
                "durable_local_write_status": "success",
                "archive_acknowledgement_status": "pending",
                "prune_status": "ok",
                "chat": {
                    "retained_generation_count": 48,
                    "retained_bytes": 524288,
                    "managed_generation_count": 48,
                    "acknowledged_generation_count": 40,
                    "unacknowledged_generation_count": 8,
                    "unacknowledged_bytes": 65536,
                    "oldest_retained_at": (NOW - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 20,
            },
            "market": {
                "updated_at": (NOW - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "ih_market_companion",
                "collection_status": "failed",
                "durable_local_write_status": "failed",
                "archive_acknowledgement_status": "unknown",
                "prune_status": "unknown",
                "market": {
                    "retained_generation_count": 96,
                    "retained_bytes": 262144,
                    "managed_generation_count": 96,
                    "acknowledged_generation_count": 94,
                    "unacknowledged_generation_count": 2,
                    "unacknowledged_bytes": 8192,
                    "oldest_retained_at": (NOW - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 12,
            },
        },
    }
    base.update(overrides)
    return base


def market_healthy_payload(**overrides: Any) -> dict[str, Any]:
    """Payload with market healthy, chat unhealthy."""
    base: dict[str, Any] = {
        "type": "idlehacking_collector_health",
        "schema_version": 1,
        "updated_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "ok",
        "chat": {
            "status": "down",
            "last_message_at": (NOW - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "messages_seen": 142,
            "writes_ok": 4555,
            "writes_failed": 4554,
        },
        "market": {
            "status": "ok",
            "last_capture_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_good_capture_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "commodities": 8,
            "books": 8,
            "pricing_status": "ok",
        },
        "volume": {"status": "ok", "last_change_at": (NOW - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"), "changes_seen": 12},
        "errors": [],
        "storage_retention": {
            "chat": {
                "updated_at": (NOW - timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "idlehacking_kb",
                "collection_status": "failed",
                "durable_local_write_status": "blocked",
                "archive_acknowledgement_status": "unknown",
                "prune_status": "unknown",
                "chat": {
                    "retained_generation_count": 48,
                    "retained_bytes": 524288,
                    "managed_generation_count": 48,
                    "acknowledged_generation_count": 40,
                    "unacknowledged_generation_count": 8,
                    "unacknowledged_bytes": 65536,
                    "oldest_retained_at": (NOW - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 20,
            },
            "market": {
                "updated_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "ih_market_companion",
                "collection_status": "success",
                "durable_local_write_status": "success",
                "archive_acknowledgement_status": "current",
                "prune_status": "ok",
                "market": {
                    "retained_generation_count": 96,
                    "retained_bytes": 262144,
                    "managed_generation_count": 96,
                    "acknowledged_generation_count": 94,
                    "unacknowledged_generation_count": 2,
                    "unacknowledged_bytes": 8192,
                    "oldest_retained_at": (NOW - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 12,
            },
        },
    }
    base.update(overrides)
    return base


def both_healthy_payload(**overrides: Any) -> dict[str, Any]:
    """Payload with both chat and market healthy."""
    base: dict[str, Any] = {
        "type": "idlehacking_collector_health",
        "schema_version": 1,
        "updated_at": (NOW - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "ok",
        "chat": {
            "status": "ok",
            "last_message_at": (NOW - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "messages_seen": 142,
            "writes_ok": 4555,
            "writes_failed": 0,
        },
        "market": {
            "status": "ok",
            "last_capture_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_good_capture_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "commodities": 8,
            "books": 8,
            "pricing_status": "ok",
        },
        "volume": {"status": "ok", "last_change_at": (NOW - timedelta(minutes=5)).strftime("%Y-%m-%dT%H:%M:%SZ"), "changes_seen": 12},
        "errors": [],
        "storage_retention": {
            "chat": {
                "updated_at": (NOW - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "idlehacking_kb",
                "collection_status": "success",
                "durable_local_write_status": "success",
                "archive_acknowledgement_status": "current",
                "prune_status": "ok",
                "chat": {
                    "retained_generation_count": 48,
                    "retained_bytes": 524288,
                    "managed_generation_count": 48,
                    "acknowledged_generation_count": 40,
                    "unacknowledged_generation_count": 8,
                    "unacknowledged_bytes": 65536,
                    "oldest_retained_at": (NOW - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 20,
            },
            "market": {
                "updated_at": (NOW - timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "ih_market_companion",
                "collection_status": "success",
                "durable_local_write_status": "success",
                "archive_acknowledgement_status": "current",
                "prune_status": "ok",
                "market": {
                    "retained_generation_count": 96,
                    "retained_bytes": 262144,
                    "managed_generation_count": 96,
                    "acknowledged_generation_count": 94,
                    "unacknowledged_generation_count": 2,
                    "unacknowledged_bytes": 8192,
                    "oldest_retained_at": (NOW - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 12,
            },
        },
    }
    base.update(overrides)
    return base


def stale_payload(**overrides: Any) -> dict[str, Any]:
    """Payload with stale data for both chat and market.

    Collection and durable write are reported as success (no active failure),
    but timestamps are beyond 2x the expected cadence so the adapter
    derives ``status: stale`` from freshness.
    """
    base: dict[str, Any] = {
        "type": "idlehacking_collector_health",
        "schema_version": 1,
        "updated_at": (NOW - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "stale",
        "chat": {
            "status": "stale",
            "last_message_at": (NOW - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "messages_seen": 142,
            "writes_ok": 4555,
            "writes_failed": 0,
        },
        "market": {
            "status": "stale",
            "last_capture_at": (NOW - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_good_capture_at": (NOW - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "commodities": 8,
            "books": 8,
        },
        "errors": ["heartbeat timed out"],
        "storage_retention": {
            "chat": {
                "updated_at": (NOW - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "idlehacking_kb",
                "collection_status": "success",
                "durable_local_write_status": "success",
                "archive_acknowledgement_status": "pending",
                "prune_status": "ok",
                "chat": {
                    "retained_generation_count": 48,
                    "retained_bytes": 524288,
                    "managed_generation_count": 48,
                    "acknowledged_generation_count": 40,
                    "unacknowledged_generation_count": 8,
                    "unacknowledged_bytes": 65536,
                    "oldest_retained_at": (NOW - timedelta(hours=12)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 20,
            },
            "market": {
                "updated_at": (NOW - timedelta(hours=4)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "workload": "ih_market_companion",
                "collection_status": "success",
                "durable_local_write_status": "success",
                "archive_acknowledgement_status": "pending",
                "prune_status": "ok",
                "market": {
                    "retained_generation_count": 96,
                    "retained_bytes": 262144,
                    "managed_generation_count": 96,
                    "acknowledged_generation_count": 94,
                    "unacknowledged_generation_count": 2,
                    "unacknowledged_bytes": 8192,
                    "oldest_retained_at": (NOW - timedelta(days=6)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                },
                "pruned_generation_count": 12,
            },
        },
    }
    base.update(overrides)
    return base
