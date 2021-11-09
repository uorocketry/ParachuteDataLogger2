#include <Arduino.h>
#include <board_comm.h>
#include <scales.h>

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    scales::init();
    delay(100);
    scales::setPower(true);

    Serial.begin(115200);
    while (Serial)
    {
        Serial.println("Press any key to read");
        while (!Serial.available()) { }

        // Flush serial buffer
        while (Serial.available())
        {
            delay(2);
            Serial.read();
        }

        board_comm::Reading reading = scales::readOnce();
        Serial.print("X: "); // Axial
        Serial.println(reading.x);
        Serial.print("Y: "); // Vertical
        Serial.println(reading.y);
        Serial.print("Z: "); // Horizontal
        Serial.println(reading.z);
        Serial.println("---");
    }
}

void loop()
{
    
}
