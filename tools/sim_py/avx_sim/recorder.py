"""Bus recorder — append-only event log with stable hash for determinism tests.

We use SHA-256 over a canonical byte stream so two runs with the same seed
produce identical hashes (SYS-024 evidence bundle replay).
"""
from __future__ import annotations
import hashlib
import struct
from dataclasses import dataclass, field


@dataclass
class Recorder:
    records: list[tuple[int, str, str, bytes]] = field(default_factory=list)
    """Each record: (ts_us, bus_id, msg_id, payload_bytes)."""

    def append(self, ts_us: int, bus_id: str, msg_id: str, payload: bytes) -> None:
        self.records.append((int(ts_us), str(bus_id), str(msg_id), bytes(payload)))

    def to_bytes(self) -> bytes:
        out = bytearray()
        out += b"AVX-REC\x01"  # magic + schema version
        out += struct.pack("<Q", len(self.records))
        for ts, bus, msg, payload in self.records:
            out += struct.pack("<Q", ts)
            bus_b = bus.encode("utf-8")
            msg_b = msg.encode("utf-8")
            out += struct.pack("<H", len(bus_b)) + bus_b
            out += struct.pack("<H", len(msg_b)) + msg_b
            out += struct.pack("<I", len(payload)) + payload
        return bytes(out)

    def sha256(self) -> str:
        return hashlib.sha256(self.to_bytes()).hexdigest()

    def __len__(self) -> int:
        return len(self.records)
