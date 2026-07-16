#!/usr/bin/env python3
"""vps_capacity_config.py — Configurable defaults and thresholds for VPS capacity evidence.

Authority-backed thresholds from:
  docs/DATA_LIFECYCLE_STANDARD.md §Disk thresholds
  docs/OPERATING_MODEL.md §Capacity evidence
  _internal/outbox/session-9/27-operational-tranche-execution.md §Capacity

Usage:
    from tools.producers.vps_capacity_config import DEFAULT_CONFIG, CapacityThresholds
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass(frozen=True)
class CapacityThresholds:
    WARN_DISK_PCT: int = 80
    STOP_DISK_PCT: int = 85
    WARN_FREE_GB: int = 7
    STOP_FREE_GB: int = 5
    STOP_INODE_PCT: int = 80
    EMERGENCY_FREE_GB: int = 1
    RESTORE_STAGING_MULTIPLIER: int = 2
    RESTORE_STAGING_BUFFER_GB: int = 1


@dataclass(frozen=True)
class CapacityConfig:
    PROJECT: str = "ivy_control_vps"
    WORKFLOW: str = "host_capacity"
    EXPECTED_CADENCE_SECONDS: int = 3600
    PRODUCER_VERSION: str = "vps_capacity_snapshot/v2"
    SSH_HOST: str = "ih-market-vps"
    SSH_TIMEOUT: int = 18
    SSH_CONNECT_TIMEOUT: str = "10"
    MODE: str = "ssh"  # "ssh" or "direct"; direct runs probes locally without SSH

    thresholds: CapacityThresholds = field(default_factory=CapacityThresholds)

    @property
    def WORKFLOW_ID(self) -> str:
        return f"{self.PROJECT}/{self.WORKFLOW}"


DEFAULT_CONFIG: CapacityConfig = CapacityConfig()
DIRECT_CONFIG: CapacityConfig = CapacityConfig(MODE="direct")
