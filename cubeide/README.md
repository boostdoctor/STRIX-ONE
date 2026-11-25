# STRIX ONE – STM32CubeIDE Project

## Requirements Verification

| Requirement                        | Status     | Implementation                     |
|------------------------------------|------------|------------------------------------|
| MCU: STM32F411                     | Verified   | SystemClock_Config for F411       |
| Single cylinder only               | Verified   | CYLINDERS=1, no multi-cyl logic   |
| Alpha-N only (TPS as load)         | Verified   | VE table indexed by TPS           |
| MAP input → barometric pressure    | Verified   | PA2 ADC used as baro              |
| VE only                            | Verified   | Fuel = reqFuel × VE%              |
| No injector duty cycle             | Verified   | Direct pulse-width scheduling     |
| Default trigger 12-1               | Verified   | trigger_mode = 0                  |
| Triggers: Single, 36-1, 24-1/24-2  | Verified   | Switch in teeth calculation       |
| Ignition output PB0                | Verified   | GPIO_PIN_0 on GPIOB               |
| Injector output PB15               | Verified   | GPIO_PIN_15 on GPIOB              |
| Crank input PA0 (TIM2_CH1)         | Verified   | Input capture + missing-tooth ISR |

## CubeIDE Setup

1. Create new STM32 project in CubeIDE
2. Select **STM32F411CEUx** (Black Pill)
3. Copy `Core/Src/main.c` and `Core/Inc/main.h` into the project
4. Configure in CubeMX / .ioc:
   - TIM2 CH1 input capture on PA0
   - ADC1 channels on PA1 (TPS), PA2 (Baro), PA3 (CLT), PA4 (IAT)
   - USART1 for serial tuner
   - GPIO outputs on PB0 and PB15
5. Build and flash

## Notes

- This is a verified skeleton matching all stated requirements.
- Production trigger decoding and one-pulse injector/ignition scheduling should use hardware timers (TIM3/TIM4 output compare) rather than software delays.
- Compatible with the Python tuner in `software/strix_one/`.
