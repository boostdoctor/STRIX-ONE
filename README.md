# STRIX ONE

**Single-cylinder only variant of TorquEFI STRIX**

Simplified Electronic Fuel Injection (EFI) ECU based on the STM32F411 microcontroller, identical MCU to the original TorquEFI STRIX.

## Design Goals

- **Single cylinder only** — Sequential injection and ignition for one cylinder
- **Alpha-N only** — Throttle Position Sensor (TPS) used as the primary load signal
- **MAP input repurposed as barometric pressure** — Used for air density correction only
- **VE only** — Volumetric Efficiency table is the sole fuel calculation method (no speed-density)
- **No Injector Duty Cycle** — Duty cycle calculation and limiting removed for simplicity
- **Trigger system** — Default 12-1 missing tooth wheel
  - Supported options:
    - Single Tooth
    - 36-1
    - 24-1 / 24-2

## Hardware

- **MCU**: STM32F411 (Cortex-M4, 100 MHz, FPU)
- Same pinout and peripheral usage as original TorquEFI STRIX where possible
- Minimum required sensors:
  - TPS (Alpha-N load)
  - MAP (used as Baro)
  - CLT (Coolant Temperature)
  - IAT (Intake Air Temperature)
  - Crank trigger (and optional cam for phase if needed)
- Outputs:
  - 1x Injector
  - 1x Ignition (smart coil or driver)

## Fuel Calculation (Alpha-N + VE)

```
PW = ReqFuel * VE(TPS, RPM) * Corrections
```

Where:
- `ReqFuel` = base pulse width for 100% VE at the configured injector
- `VE` is looked up from a 2D table (TPS % vs RPM)
- Corrections include: CLT, IAT, Barometric pressure (from MAP input), battery voltage, etc.
- Injector duty cycle is **not** calculated or enforced

## Trigger Options

| Option          | Description                          | Default |
|-----------------|--------------------------------------|---------|
| 12-1            | 12 tooth wheel with 1 missing tooth  | Yes     |
| Single Tooth    | Simple single pulse per revolution   | No      |
| 36-1            | 36 tooth with 1 missing              | No      |
| 24-1 / 24-2     | 24 tooth with 1 or 2 missing         | No      |

## Building

This project is set up for [PlatformIO](https://platformio.org/).

```bash
cd STRIX-ONE
pio run -e stm32f411
```

## Repository

All source files for this variant are intended to live in:
https://github.com/boostdoctor/STRIX-ONE.git

## Pins (confirmed)

| Function          | Pin   |
|-------------------|-------|
| Ignition output   | PB0   |
| Injector output   | PB15  |
| Crank trigger     | PA0   |
| TPS               | PA1   |
| MAP / Baro        | PA2   |
| CLT               | PA3   |
| IAT               | PA4   |

## Python Tuning Software

Exact layout matching TorquEFI STRIX (`STRIX_V2_py/strix_v2`), adapted for single-cylinder Alpha-N.

Location: `software/strix_one/`

```
strix_one/
├── __init__.py
├── constants.py          # Alpha-N / TPS bins, trigger modes
├── datalog.py
├── device_id.py
├── inc_lookup.py
├── main_window.py        # PySide6 main window (same structure)
├── protocol.py           # Status parsing for Alpha-N firmware
├── serial_worker.py
├── tcal.py
├── dashboards/
│   ├── dyno.json
│   └── street.json
├── lookups/
│   └── AEMWB.inc
└── widgets/
    ├── live_strip.py
    ├── map_view.py
    └── ... (stubs for remaining original widgets)
```

### Run

```bash
pip install -r software/requirements.txt
python -m strix_one.main_window
# or
cd software && python -m strix_one.main_window
```

Features retained from original layout:
- Live strip gauges
- Map view tabs (VE + Ignition, Alpha-N TPS×RPM)
- Trigger selection
- Serial worker + protocol
- Dark theme

Simplified for single cylinder: no multi-cylinder trim, no boost/VVT/idle maps, MAP input treated as barometric only.


## Firmware Status

- Single cylinder Alpha-N + VE
- Trigger gap detection (basic)
- Injection and ignition outputs on specified pins
- Serial status streaming


## License

To be determined (match original TorquEFI STRIX license if available).
