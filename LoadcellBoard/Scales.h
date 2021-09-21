#ifndef SCALES_H
#define SCALES_H

#include "Arduino.h"

namespace Scales {
  struct Reading {
    Reading() : x(0.0f), y(0.0f), z(0.0f) { }
    float x, y, z;
  };

  void init();
  void setPower(bool on);
  bool scalesReady();
  Reading readOnce();
}

#endif
