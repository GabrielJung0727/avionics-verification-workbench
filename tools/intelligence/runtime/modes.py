"""The three operational modes for AI output:

  Shadow              log only, no consumer touched
  Advisory            written to ack queue, never auto-applied
  LimitedSupervised   written to ack queue + on ack a low-criticality
                      service may consume the suggestion

All three keep the deterministic pipeline running unchanged.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Mode(str, Enum):
    SHADOW = "shadow"
    ADVISORY = "advisory"
    LIMITED_SUPERVISED = "limited_supervised"


@dataclass
class OperatorAck:
    ack_id: int
    ts_iso: str
    operator_role: str
    decision: str   # "accept" | "reject"
    rationale: str = ""


@dataclass
class AckQueue:
    """Items proposed by AI that need explicit operator acknowledgment.
    Shadow mode never writes here. Advisory writes but never applies.
    LimitedSupervised writes; on ack a low-criticality consumer may act."""
    pending: list[dict] = field(default_factory=list)
    acks: list[OperatorAck] = field(default_factory=list)
    payloads_by_id: dict[int, dict] = field(default_factory=dict)
    _next_id: int = 1

    def park(self, payload: dict) -> int:
        ack_id = self._next_id
        self._next_id += 1
        item = {"ack_id": ack_id, **payload}
        self.pending.append(item)
        self.payloads_by_id[ack_id] = item
        return ack_id

    def ack(self, ack_id: int, operator_role: str, decision: str,
            rationale: str = "") -> OperatorAck:
        if decision not in ("accept", "reject"):
            raise ValueError("decision must be 'accept' or 'reject'")
        ack = OperatorAck(
            ack_id=ack_id,
            ts_iso=datetime.now(timezone.utc).isoformat(timespec="seconds"),
            operator_role=operator_role,
            decision=decision,
            rationale=rationale,
        )
        self.acks.append(ack)
        # remove from pending
        self.pending = [p for p in self.pending if p["ack_id"] != ack_id]
        return ack

    def accepted(self) -> list[OperatorAck]:
        return [a for a in self.acks if a.decision == "accept"]


# ---- Mode strategies ------------------------------------------------------

class ShadowMode:
    """AI output is logged. No consumer is touched."""
    name = Mode.SHADOW

    def __init__(self):
        self.log: list[dict] = []

    def consume(self, guarded: dict, raw: dict, violations: list[str]) -> None:
        self.log.append({"guarded": guarded, "raw": raw,
                         "violations": list(violations)})


class AdvisoryMode:
    """AI output is parked in the ack queue. Even after ack, no automatic
    action is taken — the operator must perform any change manually."""
    name = Mode.ADVISORY

    def __init__(self, queue: AckQueue):
        self.queue = queue
        self.log: list[dict] = []

    def consume(self, guarded: dict, raw: dict, violations: list[str]
                ) -> int:
        ack_id = self.queue.park({"guarded": guarded, "raw": raw,
                                  "violations": list(violations)})
        self.log.append({"ack_id": ack_id, "guarded": guarded,
                         "violations": list(violations)})
        return ack_id


class LimitedSupervisedMode:
    """AI output is parked. Only after ack does a low-criticality service
    consume it. The consumer is provided by the caller and is invoked
    with the guarded payload."""
    name = Mode.LIMITED_SUPERVISED

    def __init__(self, queue: AckQueue,
                 consumer: Any | None = None,
                 allowed_consumer_keys: set[str] | None = None):
        self.queue = queue
        self.consumer = consumer
        self.allowed_consumer_keys = allowed_consumer_keys or set()
        self.log: list[dict] = []
        self.applied: list[dict] = []

    def consume(self, guarded: dict, raw: dict, violations: list[str]) -> int:
        ack_id = self.queue.park({"guarded": guarded, "raw": raw,
                                  "violations": list(violations)})
        self.log.append({"ack_id": ack_id})
        return ack_id

    def apply_if_acked(self) -> int:
        """Forward each accepted ack to the configured low-criticality
        consumer. Returns the number of payloads applied. Idempotent."""
        applied = 0
        if self.consumer is None:
            return 0
        already = {a["ack_id"] for a in self.applied}
        for ack in self.queue.accepted():
            if ack.ack_id in already:
                continue
            payload = self.queue.payloads_by_id.get(ack.ack_id)
            if payload is None:
                continue
            filtered = {k: v for k, v in payload["guarded"].items()
                        if k in self.allowed_consumer_keys}
            self.consumer(filtered)
            self.applied.append({"ack_id": ack.ack_id, "applied": filtered})
            applied += 1
        return applied
