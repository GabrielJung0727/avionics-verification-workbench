"""Avionics Verification Workbench — Python reference simulator (M2).

The Python reference is the source of truth for M2 semantics. C++ port is
deferred to M3 hot-paths once requirements stabilize.
"""

from .sim_clock import SimClock
from .scheduler import Scheduler, Partition
from .health_monitor import HealthMonitor, HmEvent
from .ipc import SamplingPort, QueuingPort
from .a429 import A429Word, encode_a429, decode_a429
from .afdx import AfdxBus, VirtualLink
from .recorder import Recorder
from .partition_loader import load_partition_table
from . import modules  # noqa: F401

__all__ = [
    "SimClock",
    "Scheduler",
    "Partition",
    "HealthMonitor",
    "HmEvent",
    "SamplingPort",
    "QueuingPort",
    "A429Word",
    "encode_a429",
    "decode_a429",
    "AfdxBus",
    "VirtualLink",
    "Recorder",
    "load_partition_table",
]
