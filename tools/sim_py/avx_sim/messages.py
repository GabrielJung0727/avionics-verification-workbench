"""ICD message dataclasses (M1 ICD v0). Schema version is encoded for SYS-019."""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum

SCHEMA_VERSION = 1


class Freshness(IntEnum):
    OK = 0
    STALE = 1
    INVALID = 2


class FccMode(IntEnum):
    OFF = 0
    NORMAL = 1
    ALTERNATE = 2
    DIRECT = 3


class AlertLevel(IntEnum):
    ADVISORY = 0
    CAUTION = 1
    WARNING = 2


@dataclass(frozen=True)
class AirData:               # MSG-001
    ts_us: int
    ias: float
    altitude: float
    vs: float
    freshness: Freshness = Freshness.OK


@dataclass(frozen=True)
class Attitude:              # MSG-002
    ts_us: int
    pitch: float
    roll: float
    yaw_rate: float
    freshness: Freshness = Freshness.OK


@dataclass(frozen=True)
class EngineRaw:             # MSG-003
    ts_us: int
    n1: float
    n2: float
    egt: float
    ff: float


@dataclass(frozen=True)
class EngineParams:          # MSG-004
    ts_us: int
    n1: float
    n2: float
    egt: float
    ff: float
    state: AlertLevel = AlertLevel.ADVISORY


@dataclass(frozen=True)
class EngineExceed:          # MSG-005
    ts_us: int
    param: str
    level: AlertLevel
    value: float
    latched: bool


@dataclass(frozen=True)
class FccModeMsg:            # MSG-006
    ts_us: int
    mode: FccMode
    reason: str
    lane_disagree: bool


@dataclass(frozen=True)
class FccCommand:            # MSG-007
    ts_us: int
    pitch_cmd: float
    roll_cmd: float
    yaw_cmd: float
    valid: bool


@dataclass(frozen=True)
class HmEventMsg:            # MSG-008
    ts_us: int
    source: str
    code: str
    severity: str
    detail: str = ""
