#include "scales.h"

#include <Arduino.h>

// HX711 Loadcell Amplifiers https://cdn.sparkfun.com/datasheets/Sensors/ForceFlex/hx711_english.pdf
#define DATA_X 8        // Axial
#define DATA_Y 7        // Vertical
#define DATA_Z 9        // Horizontal
#define SCK 10          // Loadcell Clock

#define PIN_X PINB      // Axial      D8
#define PIN_Y PIND      // Vertical   D7
#define PIN_Z PINB      // Horizontal D9
#define PORT_C PORTB    // Clock      D10

#define BIT_X B00000001 // Axial      D8
#define BIT_Y B10000000 // Vertical   D7
#define BIT_Z B00000010 // Horizontal D9
#define BIT_C B00000100 // Clock      D10

// Single clock cycle delay
#define NOP __asm__ __volatile__("nop\n\t")

namespace scales
{
    void init()
    {
        pinMode(DATA_X, INPUT);
        pinMode(DATA_Y, INPUT);
        pinMode(DATA_Z, INPUT);
        pinMode(SCK, OUTPUT);
    }

    void setPower(bool on)
    {
        digitalWrite(SCK, on);
    }

    bool scalesReady()
    {
        //return !((PIN_X & BIT_X) || (PIN_Y & BIT_Y) || (PIN_Z & BIT_Z));
        return true;
    }

    board_comm::Reading readOnce()
    {
        board_comm::Reading value;
        if (!scalesReady())
            return value;

        int32_t valX = 0;
        int32_t valY = 0;
        int32_t valZ = 0;

        cli(); // Disable inturrupts

        // Read 24 data bits
        for (int i = 23; i >= 0; i--)
        {
            PORT_C |= BIT_C;                // Clock high
            NOP; NOP; NOP; NOP; NOP;  NOP;  // Delay
            PORT_C &= ~BIT_C;               // Clock low

            valX |= ((int32_t)(PIN_X & BIT_X)) << i;
            valY |= ((int32_t)(PIN_Y & BIT_Y) >> 7) << i;
            valZ |= ((int32_t)(PIN_Z & BIT_Z) >> 1) << i;
        }

        // Clock one more time for channel A, gain 128
        PORT_C |= BIT_C;                // Clock high
        NOP; NOP; NOP; NOP; NOP;  NOP;  // Delay
        PORT_C &= ~BIT_C;               // Clock low

        sei(); // Re-enable interrupts

        // Extend 24 bit 2's complement to 32 bit
        if (valX & 0x800000)
            valX |= 0xFF000000;
        if (valY & 0x800000)
            valY |= 0xFF000000;
        if (valZ & 0x800000)
            valZ |= 0xFF000000;

        value.x = valX;
        value.y = valY;
        value.z = valZ;
        return value;
    }
}
