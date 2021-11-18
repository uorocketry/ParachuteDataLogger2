#include <Arduino.h>
#include <board_comm.h>

bool sendReading = false;
bool sendPingResponse = false;
bool ledToggle = false;

void onRecieveCommand(board_comm::Command command, board_comm::Address address)
{
    if (command == board_comm::PING_RESPONSE)
        sendPingResponse = true;
    else if (command == board_comm::READING)
        sendReading = true;
}

// Read a single byte command sent over serial
void readSerial()
{
    if(Serial.available())
    {
        switch (Serial.read())
        {
        case 1:
            board_comm::transmit(board_comm::LOADCELL, board_comm::PING);
            break;
        case 2:
            board_comm::transmit(board_comm::LOADCELL, board_comm::READ_SINGLE);
            break;
        case 3:
            board_comm::transmit(board_comm::LOADCELL, board_comm::START_LOGGING);
            break;
        case 4:
            board_comm::transmit(board_comm::LOADCELL, board_comm::STOP_LOGGING);
            break;
        }
    }
}

void setup()
{
    Serial.begin(115200);
    pinMode(LED_BUILTIN, OUTPUT);
    board_comm::init(board_comm::ANEMOMETER, onRecieveCommand);
}

void writeSerial()
{
    if (sendPingResponse)
    {
        Serial.write(1);
        sendPingResponse = false;
    }
    else if (sendReading)
    {
        board_comm::Reading reading;
        board_comm::read(reading);

        digitalWrite(LED_BUILTIN, ledToggle);
        ledToggle = !ledToggle;

        Serial.write((uint8_t *)(&reading.x), 4);
        Serial.write((uint8_t *)(&reading.y), 4);
        Serial.write((uint8_t *)(&reading.z), 4);
        sendReading = false;
    }
}

void loop()
{
    readSerial();
    writeSerial();
}
