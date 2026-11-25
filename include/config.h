#ifndef CONFIG_H
#define CONFIG_H

// STRIX ONE - Single Cylinder Alpha-N variant of TorquEFI STRIX
// MCU: STM32F411
// Pins (as specified):
//   Ignition output: PB0
//   Injector output: PB15

#define MCU_STM32F411           1
#define CYLINDERS               1
#define ALPHA_N_ONLY            1
#define VE_ONLY                 1
#define NO_INJECTOR_DUTY        1

// Pin definitions
#define PIN_IGNITION            PB0
#define PIN_INJECTOR            PB15
#define PIN_CRANK               PA0     // TIM2_CH1 input capture
#define PIN_TPS                 PA1     // ADC
#define PIN_BARO                PA2     // ADC (MAP input used as baro)
#define PIN_CLT                 PA3     // ADC
#define PIN_IAT                 PA4     // ADC
#define PIN_BATT                PA5     // ADC (optional)

// Trigger modes
enum TriggerMode {
    TRIGGER_12_1 = 0,
    TRIGGER_SINGLE = 1,
    TRIGGER_36_1 = 2,
    TRIGGER_24_1 = 3,
    TRIGGER_24_2 = 4
};

#define DEFAULT_TRIGGER         TRIGGER_12_1

// Table dimensions
#define VE_ROWS                 16
#define VE_COLS                 16
#define IGN_ROWS                16
#define IGN_COLS                16

// Engine constants
#define TEETH_PER_REV_DEFAULT   12
#define MISSING_TEETH_DEFAULT   1

#endif
