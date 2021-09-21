#include "Scales.h"

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Scales::init();
  Serial.begin(115200);
  delay(1000);
  Scales::setPower(true);
}

void loop() {
  delay(1000);
  Scales::Reading reading = Scales::readOnce();
  
  Serial.print("X: "); // Axial
  Serial.println(reading.x);
  Serial.print("Y: "); // Vertical
  Serial.println(reading.y);
  Serial.print("Z: "); // Horizontal
  Serial.println(reading.z);
  Serial.println("---");
}
