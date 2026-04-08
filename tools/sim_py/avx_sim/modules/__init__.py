"""M3 functional modules: DC, FCC, Engine I/F, Display Computer.

Each module is intentionally framework-light: a small dataclass + a ``step``
method that takes the current sim time and any inputs, returns its outputs,
and reports faults to the shared HealthMonitor. This makes per-HLR unit tests
trivial without requiring the scheduler.
"""
from .data_concentrator import DataConcentrator, SensorRange
from .engine import EngineInterface, EngineLimits, LimitState
from .fcc import Fcc, FccLaneOutput
from .display import DisplayComputer, DisplayFrame, AlertEntry

__all__ = [
    "DataConcentrator",
    "SensorRange",
    "EngineInterface",
    "EngineLimits",
    "LimitState",
    "Fcc",
    "FccLaneOutput",
    "DisplayComputer",
    "DisplayFrame",
    "AlertEntry",
]
