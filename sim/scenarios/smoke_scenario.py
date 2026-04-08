"""Smoke scenario — exercises every M1 ICD message and every IPC mechanism.

Pipeline:
    DC partition publishes AirData/Attitude/EngineRaw on A429-lite (encoded).
    FCC cmd & mon partitions consume AirData via sampling port, run a tiny
    placeholder lane, publish FccMode + FccCommand.
    ENG partition consumes EngineRaw, publishes EngineParams + EngineExceed
    on AFDX-lite VL.
    DSP partition pulls EngineParams and FccMode from AFDX VLs.
    HM partition rotates and snapshots event count into the recorder.

Used by both the determinism test and (later) the M3 functional tests.
"""
from __future__ import annotations
import struct
from dataclasses import dataclass

from avx_sim import (
    AfdxBus,
    HealthMonitor,
    Partition,
    QueuingPort,
    Recorder,
    SamplingPort,
    Scheduler,
    SimClock,
    VirtualLink,
    encode_a429,
    load_partition_table,
)
from avx_sim.a429 import A429Word, A429SSM
from avx_sim.afdx import AfdxFaults
from avx_sim.health_monitor import HmEvent

# A429 labels per ICD
LABEL_AIRDATA_IAS = 0x10
LABEL_ATTITUDE_PITCH = 0x11
LABEL_ENG_N1 = 0x20
LABEL_FCC_PITCH_CMD = 0x30

# AFDX VLs per ICD
VL_ENG_PARAMS = 0x100
VL_ENG_EXCEED = 0x101
VL_FCC_MODE = 0x110
VL_HM_EVENT = 0x1F0


@dataclass
class WorldState:
    seed: int = 42
    tick: int = 0
    ias_drift_per_tick: float = 0.0   # fault hook for tests
    inject_overrun_at: int = -1
    fcc_dc_value: float = 0.0


def build_smoke(seed: int = 42, faults: AfdxFaults | None = None,
                ias_drift: float = 0.0,
                inject_overrun_at: int = -1) -> tuple[Scheduler, Recorder, HealthMonitor, WorldState]:
    clock = SimClock()
    hm = HealthMonitor(table={
        HmEvent.PARTITION_OVERRUN: "LOG",
        HmEvent.DEADLINE_MISS: "LOG",
        HmEvent.IPC_OVERFLOW: "LOG",
        HmEvent.IPC_STALE: "LOG",
        HmEvent.LANE_DISAGREE: "LOG",
    })
    sched = Scheduler(clock=clock, hm=hm, tick_us=1000)
    recorder = Recorder()
    state = WorldState(seed=seed, ias_drift_per_tick=ias_drift,
                       inject_overrun_at=inject_overrun_at)

    # AFDX bus
    afdx = AfdxBus(hm=hm)
    afdx.add_link(VirtualLink(VL_ENG_PARAMS, bag_us=10000, name="EngParams",
                              faults=faults or AfdxFaults()))
    afdx.add_link(VirtualLink(VL_ENG_EXCEED, bag_us=10000, name="EngExceed"))
    afdx.add_link(VirtualLink(VL_FCC_MODE, bag_us=10000, name="FccMode"))
    afdx.add_link(VirtualLink(VL_HM_EVENT, bag_us=10000, name="HmEvent"))

    # IPC ports
    air_port = SamplingPort[float]("AirData.ias", freshness_budget_us=30000, hm=hm)
    eng_port = SamplingPort[float]("EngineRaw.n1", freshness_budget_us=60000, hm=hm)
    fcc_mode_q = QueuingPort[int]("FccMode.q", capacity=8, hm=hm)

    # ---- partition bodies ----
    def dc_body(now_us: int) -> None:
        # publish ias on A429
        ias = 250.0 + state.ias_drift_per_tick * state.tick
        word = encode_a429(A429Word(LABEL_AIRDATA_IAS, sdi=0,
                                    data=int(ias) & 0x3FFFF))
        recorder.append(now_us, "A429", "MSG-001",
                        struct.pack("<I", word))
        air_port.write(ias, now_us)

        # attitude
        pitch = 2  # degrees
        word2 = encode_a429(A429Word(LABEL_ATTITUDE_PITCH, sdi=0, data=pitch))
        recorder.append(now_us, "A429", "MSG-002",
                        struct.pack("<I", word2))

        # engine raw
        n1 = 88
        word3 = encode_a429(A429Word(LABEL_ENG_N1, sdi=0, data=n1))
        recorder.append(now_us, "A429", "MSG-003",
                        struct.pack("<I", word3))
        eng_port.write(float(n1), now_us)
        state.tick += 1

    def fcc_cmd_body(now_us: int) -> None:
        ias, fresh = air_port.read(now_us)
        cmd = 0.0 if (ias is None or not fresh) else (ias - 250.0) * 0.1
        state.fcc_dc_value = cmd
        word = encode_a429(A429Word(LABEL_FCC_PITCH_CMD, sdi=0,
                                    data=int(cmd) & 0x3FFFF))
        recorder.append(now_us, "A429", "MSG-007",
                        struct.pack("<I", word))
        # publish FCC mode on AFDX
        mode = 1  # NORMAL
        afdx.send(VL_FCC_MODE, struct.pack("<BI", mode, now_us & 0xFFFFFFFF), now_us)
        recorder.append(now_us, "AFDX", "MSG-006",
                        struct.pack("<BI", mode, now_us & 0xFFFFFFFF))
        fcc_mode_q.push(mode, now_us)

    def fcc_mon_body(now_us: int) -> None:
        ias, fresh = air_port.read(now_us)
        if ias is None:
            return
        mon = (ias - 250.0) * 0.1
        if abs(mon - state.fcc_dc_value) > 0.5:
            hm.record(now_us, "FCC", HmEvent.LANE_DISAGREE, "HIGH",
                      f"d={mon - state.fcc_dc_value:.3f}")

    def eng_body(now_us: int) -> None:
        n1, fresh = eng_port.read(now_us)
        if n1 is None:
            return
        afdx.send(VL_ENG_PARAMS, struct.pack("<f", float(n1)), now_us)
        recorder.append(now_us, "AFDX", "MSG-004",
                        struct.pack("<f", float(n1)))
        if n1 > 100:
            payload = struct.pack("<f", float(n1))
            afdx.send(VL_ENG_EXCEED, payload, now_us)
            recorder.append(now_us, "AFDX", "MSG-005", payload)

    def dsp_body(now_us: int) -> None:
        params = afdx.receive_due(VL_ENG_PARAMS, now_us)
        modes = afdx.receive_due(VL_FCC_MODE, now_us)
        recorder.append(now_us, "DSP", "render",
                        struct.pack("<II", len(params), len(modes)))

    def hm_body(now_us: int) -> None:
        recorder.append(now_us, "HM", "snapshot",
                        struct.pack("<I", len(hm.events)))

    bodies = {
        "P1_dc": dc_body,
        "P2_fcc_cmd": fcc_cmd_body,
        "P3_fcc_mon": fcc_mon_body,
        "P4_eng": eng_body,
        "P5_dsp": dsp_body,
        "P6_hm": hm_body,
    }

    table = load_partition_table("config/partitions/default.txt")
    for row in table:
        body = bodies[row["id"]]
        p = Partition(
            id=row["id"],
            period_us=row["period_us"],
            budget_us=row["budget_us"],
            offset_us=row["offset_us"],
            criticality=row["criticality"],
            body=body,
        )
        # optional fault: simulate overrun for one specific partition
        if inject_overrun_at >= 0 and row["id"] == "P2_fcc_cmd":
            p.simulated_exec_us = row["budget_us"] + 500
        sched.add_partition(p)

    return sched, recorder, hm, state
