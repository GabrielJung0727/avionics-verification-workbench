# Bus Design (M2)

## 1. A429-lite
- 단방향 label 메시지
- 32-bit word 흉내: label(8) + SDI(2) + data(19) + SSM(2) + parity(1)
- python/C++ 양쪽에서 encode/decode
- publisher는 rate-controlled, subscriber는 sampling
- fault hooks: drop, bit-flip, stuck-label

## 2. AFDX-lite
- UDP 기반 virtual link (VL ID = 16-bit)
- BAG (bandwidth allocation gap) 흉내: rate limiter
- redundant path는 옵션 (M4)
- fault hooks: drop, delay, reorder, duplicate

## 3. 메시지 ↔ 버스 매핑
| Msg | Bus | Encoding |
|---|---|---|
| MSG-001 AirData | A429 | label 0x10 ~ |
| MSG-002 Attitude | A429 | label 0x11 ~ |
| MSG-003 EngineRaw | A429 | label 0x20 ~ |
| MSG-004 EngineParams | AFDX | VL 0x100 |
| MSG-005 EngineExceed | AFDX | VL 0x101 |
| MSG-006 FCCMode | AFDX | VL 0x110 |
| MSG-007 FCCCommand | A429 | label 0x30 ~ |
| MSG-008 HMEvent | AFDX | VL 0x1F0 |

## 4. Recorder 포맷
- 헤더: schema version, sim seed, start ts
- 레코드: ts_us, bus_id, msg_id, payload_bytes
- 전용 binary + csv index (replay와 디버깅 양쪽 지원)

## 5. Freshness
- 메시지별 freshness budget config (`config/bus/freshness.yaml`)
- consumer는 budget 초과 시 STALE 전파
