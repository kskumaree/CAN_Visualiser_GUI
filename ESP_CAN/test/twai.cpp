#include <driver/twai.h>

#define RX_GPIO_PIN         GPIO_NUM_21
#define TX_GPIO_PIN         GPIO_NUM_22
#define BUTTON_PIN          4                // pin connected to button
#define DEFAULT_INTERVAL    1000

enum MessageCategories
{
  normal = 0,
  loopback,
  remote_transmission_request
};

static bool driver_installed = false;
enum MessageCategories category = normal;

void EXTDID_Filter(twai_filter_config_t& filter)
{
  filter.acceptance_code = 0x387B80 << 3; // Replace with the desired extended CAN ID 0xD78AB0
  filter.acceptance_mask = 0;
  filter.single_filter = true;
}

void handle_rx_message(const twai_message_t& message)
{
	Serial.print("Received New Message: ");
	dlc = message.data_length_code;
	arbid = message.identifier;
	
	// for(int i = 0; i<dlc; i++){
	// 	payload = msg.data[i] << 8
	// }

	Serial.print(dlc,HEX); Serial.print('\t'); Serial.print(arbid,HEX); Serial.print('\t');

  // for( int i=7; i>=0; i--)
  // {
  //   result <<= 8;
  //   result |= (uint64_t) message.data[i];
  // }

for (int i = 0; i < (sizeof(byte) * 8); i++)
{
   payload += ((uint64_t) message.data[i] & 0xffL) << (8 * i);
}

//   if (message.extd)
//     Serial.print("Message is in Extended Format, ");
//   else
//     Serial.print("Message is in Standard Format, ");

//   Serial2.print(message.identifier);
//   Serial2.print(" ");
//   Serial.printf("ID: %x\nBytes: ", message.identifier);
  

//   if (!message.rtr)
//   {
//     for (int i = 0; i < message.data_length_code; i++)
//     { 
//       Serial2.print(message.data[i]);
//       Serial2.print(" ");
//       Serial.printf("data[%d] = %02x, ", i, message.data[i]);
//     }
//     Serial2.println();

//     Serial.println("\n..................................................\n");
//   }

}



void setup() {
  Serial.begin(115200); // Initialize the default Serial port for debugging
//   Serial2.begin(9600, SERIAL_8N1, 17, 16); // Initialize Serial2 with baud rate 9600, 8 data bits, no parity, 1 stop bit, using pins 17 as RX and 16 as TX
  Serial2.begin(115200);
  
  twai_general_config_t general_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_GPIO_PIN, RX_GPIO_PIN, TWAI_MODE_NORMAL);
  general_config.tx_queue_len = 1000;
  general_config.rx_queue_len = 1000;

  twai_timing_config_t timing_config = TWAI_TIMING_CONFIG_125KBITS();
  
  // Extended CAN ID filter
  twai_filter_config_t filter;
  EXTDID_Filter(filter);

  if (twai_driver_install(&general_config, &timing_config, &filter) == ESP_OK)
  {
    Serial.println("Driver installed");

    if (twai_start() == ESP_OK)
    {
      Serial.println("Driver started");

      uint32_t alerts_to_enable = TWAI_ALERT_RX_DATA | TWAI_ALERT_ERR_PASS | TWAI_ALERT_BUS_ERROR | TWAI_ALERT_RX_QUEUE_FULL;

      if (twai_reconfigure_alerts(alerts_to_enable, NULL) == ESP_OK)
      {
        Serial.println("CAN alerts reconfigured");
        driver_installed = true;
      }
      else
        Serial.println("Failed to reconfigure alerts");
    }
    else
      Serial.println("Failed to start driver");
  }
  else
   Serial.println("Failed to install driver");

}

void loop() {

  if (driver_installed)
  {
    uint32_t alerts_triggered;
    twai_status_info_t status_info;

    twai_read_alerts(&alerts_triggered, pdMS_TO_TICKS(DEFAULT_INTERVAL));
    twai_get_status_info(&status_info);

    if (alerts_triggered & TWAI_ALERT_ERR_PASS)
      Serial.println("Alert: TWAI controller has become error passive.");
    else if (alerts_triggered & TWAI_ALERT_BUS_ERROR)
    {
      Serial.println("Alert: A (Bit, Stuff, CRC, Form, ACK) error has occurred on the bus.");
      Serial.printf("Bus error count: %d\n", status_info.bus_error_count);
    }
    else if (alerts_triggered & TWAI_ALERT_RX_QUEUE_FULL)
    {
      Serial.println("Alert: the RX queue is full causing received frames to be lost.");
      Serial.printf("RX buffered: %d\t", status_info.msgs_to_rx);
      Serial.printf("RX missed: %d\n", status_info.rx_missed_count);
      Serial.printf("RX overrun %d\n", status_info.rx_overrun_count);
    }
    else if (alerts_triggered & TWAI_ALERT_RX_DATA)
    {
      twai_message_t message;
      while (twai_receive(&message, 0) == ESP_OK)
        handle_rx_message(message);
    }
  }

  Serial.print(dlc,HEX); Serial.print('\t'); Serial.print(arbid,HEX); Serial.print('\t');
	
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
	// Serial.println();

  for (int i = 0; i < sizeof(serialFrame); i++) {
    Serial2.write(serialFrame[i]);
    // Serial.print(serialFrame[i],HEX);
  }

}


// 1:09:44.563 -> Received New Message: 8	387B80	AAD07008807B
// 01:09:44.563 -> AA D070 08 807B30 369CF121518 BB

// AA E470 08 807B38 0688C1014181C20 BB
                     0807000000000000

Received New Message: 48C1014181C20
02:04:38.659 -> 8	387B80	
// AA ED70 08 0387B80 48C1014181C20 BB


                     201C1814100C0868
   AA EA70 08 0387B8 0876543265 BB
                     0807000000000000