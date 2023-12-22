#include <Arduino.h>

uint8_t serialFrame[] = {
    0xAA, // Start of frame
    0xD0, 0x07, 0x00, 0x00, // Placeholder for Timestamp (Little-endian)
    0x08, // DLC (Data Length Code)
    0x01, 0x00, 0x00, 0x00, // Placeholder for Arbitration ID
    0x33, 0x22, 0x33, 0x44, // Placeholder for Payload
    0x55, 0x66, 0x77, 0x88,
    0xBB // End of frame
  };

uint8_t sof = 0xAA;
uint32_t timestamp = 2000;
uint8_t dlc = 8;
uint32_t arbid = 1;
uint64_t payload = 100;
uint8_t eof = 0xBB;

void setup() {
  Serial.begin(115200); // Adjust baud rate as needed
}

void loop() {
  // Create Serial Message Frame data

  for(int i = 0; i<8; i++){
    if(i<4){
      serialFrame[1+i] = timestamp >> (8*i);
      serialFrame[10+i] = payload >> (8*i);
      serialFrame[6+i] = arbid >> (8*i);
    }
    else{
      serialFrame[10+i] = payload >> (8*i);
    }
  }

  timestamp++;

  payload+=100;

  arbid++;

  if(arbid>6){
    arbid = 1;
  }


  // Send the updated Serial Message Frame
  for (int i = 0; i < sizeof(serialFrame); i++) {
    Serial.write(serialFrame[i]);
    // Serial.print(serialFrame[i],HEX);
  }

  delay(50); // Adjust delay as needed





