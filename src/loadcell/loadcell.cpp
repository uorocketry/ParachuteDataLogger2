#include <Arduino.h>
#include <scales.h>

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    scales::init();
    Serial.begin(115200);
    delay(1000);
    scales::setPower(true);
}

void loop()
{
    delay(1000);
    scales::Reading reading = scales::readOnce();

    Serial.print("X: "); // Axial
    Serial.println(reading.x);
    Serial.print("Y: "); // Vertical
    Serial.println(reading.y);
    Serial.print("Z: "); // Horizontal
    Serial.println(reading.z);
    Serial.println("---");
}
