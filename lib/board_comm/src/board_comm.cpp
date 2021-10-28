#include "board_comm.h"

#include <Arduino.h>
#include <Wire.h>

#define DI2C_EN 4 // Enable pin for PCA9615 DI2C IC

namespace board_comm
{
    uint8_t thisAddress;
    void (*recieveCallback)(Command command, Address address);

    void init(Address address, void (*recieveCallback)(Command, Address))
    {
        board_comm::thisAddress = address;
        board_comm::recieveCallback = recieveCallback;
        pinMode(DI2C_EN, OUTPUT);
        digitalWrite(DI2C_EN, HIGH);
        Wire.setTimeout(400);
        Wire.begin((uint8_t)address);
        Wire.onReceive(onRecieve);
    }

    // Transmit a command
    void transmit(Address address, Command command)
    {
        Wire.beginTransmission((uint8_t)address);
        Wire.write((uint8_t)command);
        Wire.write((uint8_t)thisAddress);
        Wire.endTransmission();
    }

    // Transmit a command and data
    void transmit(Address address, Command command, uint8_t *data, size_t len)
    {
        Wire.beginTransmission((uint8_t)address);
        Wire.write((uint8_t)command);
        Wire.write((uint8_t)thisAddress);
        Wire.write(data, len);
        Wire.endTransmission();
    }

    // Transmit a command and data
    void transmit(Address address, Command command, float *data, size_t len)
    {
        transmit(address, command, (uint8_t *)data, len*4);
    }

    // Call callback with the recieved command and sender address
    void onRecieve(int len)
    {
        if (Wire.available() < 2)
            return;

        Command command = (Command)Wire.read();
        Address address = (Address)Wire.read();
        recieveCallback(command, address);
    }

    // Read the specified number of bytes into the buffer
    // Call this function after onRecieve to get any data sent after the command
    bool read(uint8_t *buffer, size_t len) 
    {
        for (size_t i = 0; i < len; i++)
        {
            if (!Wire.available())
                return false;
            buffer[i] = Wire.read();
        }

        if (!Wire.available())
            return true;

        // Flush wire buffer if excess bytes were sent
        while (Wire.available())
            Wire.read();
        return false;
    }

    // Read the specified number of floats into the buffer
    // Call this function after onRecieve to get any data sent after the command
    bool read(float *buffer, size_t len)
    {
        return read((uint8_t *)buffer, len*4);
    }
}
