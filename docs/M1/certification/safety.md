# Safety Analysis (M1 v0)

> 학습 목적의 safety seed 문서. 인증 산출물이 아님.

## 1. Failure Conditions (FC)
ARP4761 스타일 분류. severity는 가정값.

| ID | Failure Condition | Effect | Severity (assumed) | Mitigation |
|---|---|---|---|---|
| FC-01 | Loss of attitude data | FCC degraded → ALTERNATE | Major | dual source + freshness check, mode reversion |
| FC-02 | Erroneous attitude data (undetected) | Wrong control command | Hazardous | cross-check, lane disagree → ALTERNATE |
| FC-03 | Loss of air data | Speed/altitude blank on DSP | Major | freshness flag + dashed display |
| FC-04 | Erroneous air data | Wrong envelope protection | Hazardous | range/rate check, monitor lane |
| FC-05 | FCC command lane crash | No control command | Hazardous | partition restart, monitor lane takes over |
| FC-06 | FCC monitor lane crash | Loss of monitor coverage | Major | HM detect, force ALTERNATE |
| FC-07 | Engine exceedance not annunciated | Crew unaware | Major | latch + DSP alert |
| FC-08 | DSP refresh drop | Stale flight info | Major | freshness check, DSP self-monitor |
| FC-09 | Partition overrun (any) | Schedule jitter, possible miss | Major | budget enforce, HM event |
| FC-10 | Bus storm / latency spike | Stale data system-wide | Major | freshness propagation, degraded mode |
| FC-11 | Health monitor failure | Loss of fault visibility | Hazardous | HM self-monitor, watchdog |
| FC-12 | Mode confusion (annunciation lag) | Pilot wrong mental model | Major | 100 ms annunciation budget, HF eval |

## 2. DAL 가정 근거
| Module | DAL (assumed) | 근거 |
|---|---|---|
| FCC cmd lane | B | Hazardous FC (FC-02, FC-05) 1st line |
| FCC mon lane | B | Hazardous FC (FC-06) 1st line, lane diversity |
| Health Monitor | B | FC-11 mitigation provider |
| Engine I/F | C | Major FC (FC-07) |
| Display Computer | C | Major FC (FC-08, FC-12) |
| Data Concentrator | C | Major FC (FC-01, FC-03) |

## 3. 안전 속성 → 요구사항 매핑 (요약)
| Property | 매핑 SYS/HLR |
|---|---|
| Lane diversity | SYS-020, HLR-FCC-002 |
| Safe state on dual fault | SYS-021, HLR-FCC-004 |
| Partition containment | SYS-004, HLR-HM-001/004 |
| Mode awareness | SYS-030, HLR-FCC-005, HLR-DSP-003 |
| Freshness propagation | SYS-002, HLR-DC-002, HLR-DSP-005 |

## 4. 다음 단계 (M3+)
- LLR 진입 시 각 FC에 대응 함수 식별
- MC/DC 대상 함수 명시
- fault campaign config로 FC 검증
