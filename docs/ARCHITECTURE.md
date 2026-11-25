# STRIX ONE Architecture Notes

## Fuel System (Alpha-N + VE Only)

- Load signal = TPS (0-100%)
- Base fuel = Required Fuel (ReqFuel) × VE from 2D table
- MAP sensor input is used **only** as barometric pressure for density correction
- No speed-density path exists
- Injector duty cycle calculation is removed. Pulse width is calculated purely from the VE model. Hardware must be sized so that duty stays within safe limits under all conditions.

## Trigger Decoding

Supported patterns (compile-time or runtime selectable):

1. **12-1** (default) — Classic missing-tooth wheel. Sync on the long gap.
2. **Single Tooth** — One pulse per crank revolution. Simple but lower resolution.
3. **36-1** — Higher resolution missing tooth.
4. **24-1 / 24-2** — Common motorcycle patterns.

For single cylinder, phase can be established from the missing tooth alone if the wheel is mounted correctly relative to TDC, or with an optional cam sensor.

## Suggested Next Implementation Steps

1. Timer input capture for crank trigger (TIM2 or TIM3 on STM32F411)
2. Gap-ratio sync for missing-tooth patterns
3. ADC DMA for continuous sensor reading (TPS, Baro, CLT, IAT, Batt)
4. Output compare / one-pulse mode for injector and ignition
5. 16×16 VE and Ignition tables with bilinear interpolation
6. Correction factors: CLT enrichment, IAT, Barometric, Battery voltage
7. TunerStudio-compatible serial protocol (optional, for tuning)
8. Non-volatile storage of tables (EEPROM or Flash emulation)

## Pin Suggestions (to match original STRIX as closely as possible)

These are placeholders — confirm against original TorquEFI STRIX schematic:

- Crank Trigger → TIM2_CH1 (PA0 or PA5)
- Injector → TIM1_CH1 (PA8)
- Ignition → TIM1_CH2 (PA9)
- TPS → ADC1_IN0 (PA0) — note conflict, choose free ADC
- MAP/Baro → ADC1_IN1
- CLT → ADC1_IN2
- IAT → ADC1_IN3

Exact pins should be taken from the original STRIX board layout.
