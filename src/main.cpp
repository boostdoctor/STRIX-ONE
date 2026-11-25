#include <Arduino.h>
#include "config.h"

// =============================================================================
// STRIX ONE Firmware
// Single-cylinder Alpha-N only | STM32F411 | VE only | No injector duty
// Ignition: PB0 | Injector: PB15
// =============================================================================

// ---------- Global state ----------
volatile uint32_t toothCount = 0;
volatile uint32_t lastToothTime = 0;
volatile uint16_t rpm = 0;
volatile uint16_t tps = 0;          // 0-1000 (0.1%)
volatile uint16_t baro = 1013;      // hPa
volatile int16_t  clt = 80;         // °C
volatile int16_t  iat = 25;         // °C
volatile uint16_t batt = 140;       // 14.0 V * 10

volatile bool synced = false;
volatile uint8_t triggerMode = DEFAULT_TRIGGER;

// VE table (TPS% vs RPM) - 16x16, values 0-120
uint8_t veTable[VE_ROWS][VE_COLS];

// Ignition table (degrees BTDC)
uint8_t ignTable[IGN_ROWS][IGN_COLS];

// ---------- Serial protocol (simple binary + text) ----------
#define CMD_GET_STATUS  'S'
#define CMD_GET_VE      'V'
#define CMD_SET_VE      'v'
#define CMD_SET_TRIGGER 'T'

void sendStatus() {
  Serial.print("RPM:"); Serial.print(rpm);
  Serial.print(",TPS:"); Serial.print(tps);
  Serial.print(",BARO:"); Serial.print(baro);
  Serial.print(",CLT:"); Serial.print(clt);
  Serial.print(",IAT:"); Serial.print(iat);
  Serial.print(",SYNC:"); Serial.print(synced ? 1 : 0);
  Serial.print(",TRIG:"); Serial.println(triggerMode);
}

// ---------- Trigger interrupt (TIM2 CH1 on PA0) ----------
void crankISR() {
  uint32_t now = micros();
  uint32_t delta = now - lastToothTime;
  lastToothTime = now;

  if (delta > 100 && delta < 100000) {  // basic filtering
    toothCount++;
    // Simple missing-tooth detection for 12-1 / 36-1 / 24-1
    if (delta > (lastDelta * 1.8f)) {   // gap roughly 2x
      synced = true;
      toothCount = 0;
    }
    lastDelta = delta;
    if (synced && toothCount > 0) {
      rpm = 60000000UL / (delta * teethPerRev());
    }
  }
}

static uint32_t lastDelta = 1000;
uint8_t teethPerRev() {
  switch (triggerMode) {
    case TRIGGER_12_1:  return 12;
    case TRIGGER_36_1:  return 36;
    case TRIGGER_24_1:
    case TRIGGER_24_2:  return 24;
    case TRIGGER_SINGLE: return 1;
    default: return 12;
  }
}

// ---------- Fuel & Ignition calculation ----------
float lookupVE(uint16_t tpsPct, uint16_t rpmVal) {
  // Bilinear interpolation placeholder
  int row = constrain(tpsPct / 6, 0, VE_ROWS - 1);   // ~0-100% -> 0-15
  int col = constrain(rpmVal / 500, 0, VE_COLS - 1); // 0-8000 rpm
  return veTable[row][col];
}

void scheduleInjection(float pw_ms) {
  // Simple software pulse for single cylinder (production should use timer one-pulse)
  digitalWrite(PIN_INJECTOR, HIGH);
  delayMicroseconds((uint32_t)(pw_ms * 1000));
  digitalWrite(PIN_INJECTOR, LOW);
}

void scheduleIgnition(float advance_deg) {
  // Placeholder - real implementation uses output compare relative to TDC
  digitalWrite(PIN_IGNITION, HIGH);
  delayMicroseconds(1000);  // dummy dwell
  digitalWrite(PIN_IGNITION, LOW);
}

// ---------- Setup ----------
void setup() {
  pinMode(PIN_IGNITION, OUTPUT);
  pinMode(PIN_INJECTOR, OUTPUT);
  digitalWrite(PIN_IGNITION, LOW);
  digitalWrite(PIN_INJECTOR, LOW);

  pinMode(PIN_CRANK, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_CRANK), crankISR, RISING);

  analogReadResolution(12);

  // Default conservative VE table (~60-80%)
  for (int r = 0; r < VE_ROWS; r++) {
    for (int c = 0; c < VE_COLS; c++) {
      veTable[r][c] = 50 + (r * 2) + (c / 2);
      ignTable[r][c] = 15 + (c / 2);  // basic advance
    }
  }

  Serial.begin(115200);
  delay(200);
  Serial.println("STRIX ONE v1.0 - Single Cylinder Alpha-N");
  Serial.println("Ignition: PB0 | Injector: PB15 | Trigger: PA0");
  Serial.println("Ready.");
}

// ---------- Main loop ----------
void loop() {
  // Sensor reads
  tps  = map(analogRead(PIN_TPS), 0, 4095, 0, 1000);
  baro = map(analogRead(PIN_BARO), 0, 4095, 800, 1100);
  clt  = map(analogRead(PIN_CLT), 0, 4095, -40, 140);
  iat  = map(analogRead(PIN_IAT), 0, 4095, -40, 140);

  // Alpha-N fuel calculation
  float ve = lookupVE(tps / 10, rpm);
  float reqFuel = 4.0f;                 // ms base (tune this)
  float pw = reqFuel * (ve / 100.0f);
  // Simple corrections
  if (clt < 60) pw *= 1.3f;
  if (baro < 980) pw *= (1013.0f / baro);

  // Fire once per revolution when synced (single cylinder)
  static uint32_t lastFire = 0;
  if (synced && (micros() - lastFire > (60000000UL / max(rpm, 100)))) {
    lastFire = micros();
    scheduleInjection(pw);
    scheduleIgnition(15.0f);
  }

  // Serial command handler
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd == CMD_GET_STATUS) sendStatus();
    else if (cmd == 'T') {               // set trigger
      while (!Serial.available());
      triggerMode = Serial.read() - '0';
      synced = false;
      Serial.println("OK");
    }
  }

  static uint32_t lastPrint = 0;
  if (millis() - lastPrint > 500) {
    lastPrint = millis();
    sendStatus();
  }
}
