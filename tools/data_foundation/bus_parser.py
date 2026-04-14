"""Parse the AVX-REC byte stream produced by ``avx_sim.recorder.Recorder`` so
that ``bus_recording.bin`` can be exploded into ``telemetry_event`` rows.

This is intentionally a no-dependency reader so the data layer never imports
the runtime package.
"""
from __future__ import annotations
import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TelemetryEvent:
    ts_us: int
    bus: str
    msg_id: str
    payload_sha256: str
    payload_len: int


def parse_bus_recording(data: bytes) -> Iterable[TelemetryEvent]:
    if data[:8] != b"AVX-REC\x01":
        raise ValueError("not an AVX-REC stream")
    pos = 8
    (count,) = struct.unpack_from("<Q", data, pos); pos += 8
    for _ in range(count):
        (ts,) = struct.unpack_from("<Q", data, pos); pos += 8
        (bus_len,) = struct.unpack_from("<H", data, pos); pos += 2
        bus = data[pos:pos + bus_len].decode("utf-8"); pos += bus_len
        (msg_len,) = struct.unpack_from("<H", data, pos); pos += 2
        msg = data[pos:pos + msg_len].decode("utf-8"); pos += msg_len
        (payload_len,) = struct.unpack_from("<I", data, pos); pos += 4
        payload = data[pos:pos + payload_len]; pos += payload_len
        yield TelemetryEvent(
            ts_us=ts,
            bus=bus,
            msg_id=msg,
            payload_sha256=hashlib.sha256(payload).hexdigest(),
            payload_len=payload_len,
        )


def parse_bus_recording_file(path: Path) -> Iterable[TelemetryEvent]:
    return parse_bus_recording(path.read_bytes())
