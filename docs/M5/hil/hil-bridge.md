# HIL-lite Bridge (M5)

## 구성
- 워크벤치 ↔ MCU/SBC 1대 (예: STM32, RPi)
- 전송: UART 또는 UDP over Ethernet
- 시간 동기: 워크벤치가 master tick, MCU는 sync 메시지 기반 local clock

## I/O 매핑
| 워크벤치 stub | 물리 핀 | 방향 |
|---|---|---|
| AirData.ias 입력 | DAC0 → MCU ADC0 | sim → MCU |
| Attitude.pitch 입력 | DAC1 → MCU ADC1 | sim → MCU |
| Actuator pitch_cmd 출력 | MCU PWM0 → loopback ADC | MCU → sim |

## 메시지
- `HIL_SYNC` (sim → MCU): tick id, t_us, seed
- `HIL_INPUT` (sim → MCU): 입력 set
- `HIL_OUTPUT` (MCU → sim): 출력 set
- `HIL_HEALTH` (MCU → sim): cycle ok, miss count

## 측정 항목
- end-to-end latency: input publish → output ack
- jitter: cycle 간격 분포
- packet drop / clock skew
- reboot recovery 시간

## Fault hooks
- packet drop
- artificial clock skew
- forced reboot
- brownout 흉내 (전원 단속)

## 결과
- HIL run도 evidence bundle에 동일 포맷으로 포함
