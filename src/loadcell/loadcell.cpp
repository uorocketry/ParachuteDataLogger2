#include <Arduino.h>
#include <board_comm.h>
#include "scales.h"

board_comm::Address pingResponse = board_comm::NONE;

void onRecieveCommand(board_comm::Command command, board_comm::Address address)
{
    Serial.print("Recieved command ");
    Serial.print(command);
    Serial.print(" from ");
    Serial.println(address);

    if (command == board_comm::PING)
        pingResponse = address;
}

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    scales::init();
    board_comm::init(board_comm::LOADCELL, onRecieveCommand);
    Serial.begin(115200);

    delay(1000);
    scales::setPower(true);
}

void loop()
{
    if (pingResponse != board_comm::NONE)
    {
        board_comm::transmit((board_comm::Address)pingResponse, board_comm::RESPONSE);
        pingResponse = board_comm::NONE;
    }

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
