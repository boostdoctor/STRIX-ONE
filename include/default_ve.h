// Default VE table for STRIX ONE (Alpha-N)
// Rows = TPS (0-100%), Columns = RPM
// Values are VE % (0-255, typically 0-120)

// This is a conservative starting map for a small single-cylinder engine.
// Tune on the dyno / road.

#ifndef DEFAULT_VE_H
#define DEFAULT_VE_H

#include "config.h"

// Simplified flat 70% starting point (to be expanded to full 16x16)
const uint8_t defaultVETable[VE_TABLE_TPS_SIZE][VE_TABLE_RPM_SIZE] = {
  // Low TPS (idle)
  {40, 42, 45, 48, 50, 52, 55, 58, 60, 62, 65, 68, 70, 72, 75, 78},
  {42, 45, 48, 50, 52, 55, 58, 60, 62, 65, 68, 70, 72, 75, 78, 80},
  // ... remaining rows should be filled based on engine
  // For skeleton we use a simple pattern
};

#endif
