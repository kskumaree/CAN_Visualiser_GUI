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
uint32_t timestamp = 1;
uint8_t dlc = 3;
uint32_t arbid = 0;
uint64_t payload = 0;
uint8_t eof = 0xBB;

uint8_t phase1 = 0;
uint8_t phase2 = 85;
uint8_t phase3 = 170;

uint8_t phase[3] = {0,0,0};

void setup() {
  Serial.begin(921600); // Adjust baud rate as needed
}

void loop() {

  timestamp = micros();

  arbid++;
  if(arbid>2){
    arbid = 1;
  }

  // payload++;
  // if(payload>200){
  //   payload = 0;
  // }

  phase[0]++; phase[1]++; phase[2]++;

  if(phase[0]>84){
    phase[0] = 0;
  }
  if(phase[1]>170){
    phase[1] = 85;
  }
  if(phase[2]>254){
    phase[2] = 170;
  }
  
  // // Create Serial Message Frame data
  // for(int i = 0; i<8; i++){
  //   if(i<4){
  //     serialFrame[1+i] = timestamp >> (8*i);
  //     serialFrame[10+i] = payload >> (8*i);
  //     serialFrame[6+i] = arbid >> (8*i);
  //   }
  //   else{
  //     serialFrame[10+i] = payload >> (8*i);
  //   }
  // }

  Serial.write(sof);
  for(int i =0; i<4; i++){
    // serialFrame[1+i] = timestamp >> (8*i);
    // serialFrame[6+i] = arbid >> (8*i);

    Serial.write(timestamp >> (8*i));
  }
  Serial.write(dlc);
  for(int i =0; i<4; i++){
    // serialFrame[1+i] = timestamp >> (8*i);
    // serialFrame[6+i] = arbid >> (8*i);

    Serial.write((arbid >> (8*i)));
  }
  for(int i =0; i<dlc; i++){
    // serialFrame[1+i] = timestamp >> (8*i);
    // serialFrame[6+i] = arbid >> (8*i);

    Serial.write(phase[i]);
  }
  Serial.write(eof);
  delay(1);

  // // Send the updated Serial Message Frame
  // for (int i = 0; i < sizeof(serialFrame); i++) {
  //   Serial.write(serialFrame[i]);
  //   // Serial.print(serialFrame[i],HEX);
  // }
  // // Serial.println();
  // // delay(50); // Adjust delay as needed

}


