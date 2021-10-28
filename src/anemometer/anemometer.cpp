#include <Arduino.h>
#include <board_comm.h>

void onRecieveCommand(board_comm::Command command, board_comm::Address address)
{
    if (command == board_comm::RESPONSE && address == board_comm::LOADCELL)
    {
        Serial.println("Reply from loadcell board");
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    board_comm::init(board_comm::ANEMOMETER, onRecieveCommand);
}

void loop()
{
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
    board_comm::transmit(board_comm::LOADCELL, board_comm::PING);
}
