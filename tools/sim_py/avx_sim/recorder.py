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

    # ---- replay ---------------------------------------------------------
    @classmethod
    def from_bytes(cls, data: bytes) -> "Recorder":
        """Reconstruct a Recorder from a byte stream produced by to_bytes()."""
        if data[:8] != b"AVX-REC\x01":
            raise ValueError("not an AVX-REC stream")
        pos = 8
        (count,) = struct.unpack_from("<Q", data, pos); pos += 8
        rec = cls()
        for _ in range(count):
            (ts,) = struct.unpack_from("<Q", data, pos); pos += 8
            (bus_len,) = struct.unpack_from("<H", data, pos); pos += 2
            bus = data[pos:pos + bus_len].decode("utf-8"); pos += bus_len
            (msg_len,) = struct.unpack_from("<H", data, pos); pos += 2
            msg = data[pos:pos + msg_len].decode("utf-8"); pos += msg_len
            (payload_len,) = struct.unpack_from("<I", data, pos); pos += 4
            payload = bytes(data[pos:pos + payload_len]); pos += payload_len
            rec.records.append((ts, bus, msg, payload))
        return rec

    def iter_replay(self, bus: str | None = None, msg: str | None = None):
        """Yield records in timestamp order, optionally filtered by bus / msg.
        Drives downstream replay consumers deterministically."""
        for ts, b, m, payload in self.records:
            if bus is not None and b != bus:
                continue
            if msg is not None and m != msg:
                continue
            yield ts, b, m, payload
