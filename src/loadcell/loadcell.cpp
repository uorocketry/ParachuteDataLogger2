#include <Arduino.h>
#include <board_comm.h>
#include <scales.h>

board_comm::Address pingResponse = board_comm::NONE;
bool readOnce = false;

void onRecieveCommand(board_comm::Command command, board_comm::Address address)
{
    if (command == board_comm::PING)
        pingResponse = address;
    if (command == board_comm::READ_SINGLE)
        readOnce = true;
}

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);
    scales::init();
    board_comm::init(board_comm::LOADCELL, onRecieveCommand);
    scales::setPower(true);
}

void loop()
{
    if (pingResponse != board_comm::NONE)
    {
        board_comm::transmit(pingResponse, board_comm::PING_RESPONSE);
        pingResponse = board_comm::NONE;
    }
    else if (readOnce)
    {
        board_comm::Reading reading = scales::readOnce();
        board_comm::transmit(board_comm::ANEMOMETER, board_comm::READING, reading);
        readOnce = false;
    }
}
