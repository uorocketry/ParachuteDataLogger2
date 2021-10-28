#ifndef BOARD_COMM_H
#define BOARD_COMM_H

#include <Arduino.h>
#include <Wire.h>

namespace board_comm
{
    enum Address
    {
        NONE,
        ANEMOMETER,
        LOADCELL
    };

    enum Command
    {
        PING,
        RESPONSE,
        START_LOGGING,
        STOP_LOGGING,
        READ_SINGLE,
        SET_SCALE,
        ZERO,
    };

    void init(Address address, void (*recieveCallback)(Command command, Address address));
    void transmit(Address address, Command command);
    void transmit(Address address, Command command, uint8_t *data, size_t len);
    void transmit(Address address, Command command, float *data, size_t len);
    bool read(uint8_t *buffer, size_t len);
    bool read(float *buffer, size_t len);
    void onRecieve(int numBytes);
};

#endif
