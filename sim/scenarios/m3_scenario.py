"""M3 integration scenario.

Wires the four real M3 modules through the AFDX-lite bus and the IMA-style
scheduler. Used by integration tests and (later) the M4 verification runner.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from avx_sim import (
    AfdxBus,
    HealthMonitor,
    Partition,
    Recorder,
    Scheduler,
    SimClock,
    VirtualLink,
    load_partition_table,
)
from avx_sim.afdx import AfdxFaults
from avx_sim.health_monitor import HmEvent
from avx_sim.messages import AirData, Attitude, EngineRaw, Freshness
from avx_sim.modules import (
    DataConcentrator,
    DisplayComputer,
    EngineInterface,
    Fcc,
    SensorRange,
)


VL_ENG_PARAMS = 0x100
VL_ENG_EXCEED = 0x101
VL_FCC_MODE = 0x110


@dataclass
class M3World:
    seed: int = 42
    ias_drift_per_tick: float = 0.0
    egt_at_t1s: float | None = None
    n1_at_t1s: float | None = None
    force_dual_fault_at_us: int = -1
    afdx_faults: AfdxFaults = field(default_factory=AfdxFaults)


def build_m3(world: M3World | None = None
             ) -> tuple[Scheduler, Recorder, HealthMonitor, dict]:
    world = world or M3World()
    clock = SimClock()
    hm = HealthMonitor()
    sched = Scheduler(clock=clock, hm=hm, tick_us=1000)
    rec = Recorder()

    afdx = AfdxBus(hm=hm)
    afdx.add_link(VirtualLink(VL_ENG_PARAMS, bag_us=10_000, name="EngParams",
                              faults=world.afdx_faults))
    afdx.add_link(VirtualLink(VL_ENG_EXCEED, bag_us=10_000, name="EngExceed"))
    afdx.add_link(VirtualLink(VL_FCC_MODE, bag_us=10_000, name="FccMode"))

    dc = DataConcentrator(
        source_id="L", hm=hm,
        air_range=SensorRange(0, 600),
        pitch_range=SensorRange(-90, 90),
        n1_range=SensorRange(0, 110),
    )
    fcc = Fcc(hm=hm)
    eng = EngineInterface(hm=hm)
    dsp = DisplayComputer()

    state = {"tick": 0, "last_air": None, "last_att": None,
             "last_fcc_mode_ts": -1}

    def dc_body(now_us: int) -> None:
        ias = 250.0 + world.ias_drift_per_tick * state["tick"]
        air = dc.publish_air_data(ias, 10000, 0, now_us)
        att = dc.publish_attitude(2.0, 0.0, 0.0, now_us)
        # engine raw values can ramp up over time
        n1 = 88.0 if state["tick"] < 1000 else 102.0  # cross caution at ~1s
        if world.n1_at_t1s is not None and now_us >= 1_000_000:
            n1 = world.n1_at_t1s
        egt = 700.0
        if world.egt_at_t1s is not None and now_us >= 1_000_000:
            egt = world.egt_at_t1s
        eng_raw = dc.publish_engine_raw(n1, 95, egt, 3000, now_us)
        state["last_air"] = air
        state["last_att"] = att
        state["last_eng_raw"] = eng_raw
        rec.append(now_us, "DC", "MSG-001", b"\x00")
        rec.append(now_us, "DC", "MSG-002", b"\x00")
        rec.append(now_us, "DC", "MSG-003", b"\x00")
        state["tick"] += 1

    def fcc_body(now_us: int) -> None:
        air = state.get("last_air")
        att = state.get("last_att")
        dual = (world.force_dual_fault_at_us >= 0
                and now_us >= world.force_dual_fault_at_us)
        cmd, mode_msg = fcc.step(air, att, now_us, dual_sensor_fault=dual)
        rec.append(now_us, "FCC", "MSG-007", bytes([1 if cmd.valid else 0]))
        if mode_msg is not None:
            afdx.send(VL_FCC_MODE, b"\x00", now_us)
            rec.append(now_us, "FCC", "MSG-006", bytes([int(mode_msg.mode)]))
            state["last_fcc_mode_ts"] = now_us

    def fcc_mon_body(now_us: int) -> None:
        # mon lane already runs inside Fcc.step; this partition exists to
        # exercise scheduler period diversity (HLR-FCC-002 lane separation
        # is timed independently of cmd lane).
        pass

    def eng_body(now_us: int) -> None:
        raw = state.get("last_eng_raw")
        if raw is None:
            return
        params, events = eng.step(raw, now_us)
        afdx.send(VL_ENG_PARAMS, b"\x00", now_us)
        rec.append(now_us, "ENG", "MSG-004", bytes([int(params.state)]))
        for ev in events:
            afdx.send(VL_ENG_EXCEED, b"\x00", now_us)
            rec.append(now_us, "ENG", "MSG-005", bytes([int(ev.level)]))
            dsp.receive_engine_exceed(ev)
        dsp.receive_engine_params(params, now_us)

    def dsp_body(now_us: int) -> None:
        # consume mode messages
        for _ in afdx.receive_due(VL_FCC_MODE, now_us):
            from avx_sim.messages import FccModeMsg
            dsp.receive_mode(FccModeMsg(state["last_fcc_mode_ts"],
                                        fcc.mode, "", False), now_us)
        air = state.get("last_air")
        if air is not None:
            dsp.receive_air_data(air.ias, air.ts_us, air.freshness)
        frame = dsp.render(now_us)
        rec.append(now_us, "DSP", "render", bytes([len(frame.alerts)]))

    def hm_body(now_us: int) -> None:
        rec.append(now_us, "HM", "snapshot", bytes([len(hm.events) & 0xFF]))

    bodies = {
        "P1_dc": dc_body,
        "P2_fcc_cmd": fcc_body,
        "P3_fcc_mon": fcc_mon_body,
        "P4_eng": eng_body,
        "P5_dsp": dsp_body,
        "P6_hm": hm_body,
    }

    table = load_partition_table("config/partitions/default.txt")
    for row in table:
        sched.add_partition(Partition(
            id=row["id"],
            period_us=row["period_us"],
            budget_us=row["budget_us"],
            offset_us=row["offset_us"],
            criticality=row["criticality"],
            body=bodies[row["id"]],
        ))

    handles = {"dc": dc, "fcc": fcc, "eng": eng, "dsp": dsp, "afdx": afdx,
               "state": state}
    return sched, rec, hm, handles
