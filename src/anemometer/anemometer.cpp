#include <Arduino.h>
#include <board_comm.h>

bool sendPingResponse = false;
void onRecieveCommand(board_comm::Command command, board_comm::Address address)
{
    if (command == board_comm::RESPONSE && address == board_comm::LOADCELL)
    {
        sendPingResponse = true;
    }
}

// Read a single byte command sent over serial
void readSerial()
{
    if(Serial.available())
    {
        if (Serial.read() == 1)
        {
            board_comm::transmit(board_comm::LOADCELL, board_comm::PING);
        }
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    board_comm::init(board_comm::ANEMOMETER, onRecieveCommand);
    digitalWrite(LED_BUILTIN, HIGH);
}

void writeSerial()
{
    if (sendPingResponse)
    {
        Serial.write(1);
        sendPingResponse = false;
    }
}

void loop()
{
    readSerial();
    writeSerial();
}
