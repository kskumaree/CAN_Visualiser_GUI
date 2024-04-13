#include <stdio.h>
#include <stdlib.h>
#include "string.h"
#include <inttypes.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>
#include <freertos/queue.h>
#include "freertos/event_groups.h"
#include <driver/uart.h>
#include "driver/gptimer.h"
#include "driver/twai.h"
#include "esp_log.h"

/*Configuration Settings*/
enum { BUF_LEN = 20 };

/*Pins*/
// #define TXD_PIN (GPIO_NUM_16)
// #define RXD_PIN (GPIO_NUM_17)

#define TX_GPIO_NUM                     GPIO_NUM_22
#define RX_GPIO_NUM                     GPIO_NUM_21

#define TXD_PIN (GPIO_NUM_1)
#define RXD_PIN (GPIO_NUM_3)

/*Globals*/

#define UART_NUM UART_NUM_0
#define BUF_SIZE (1024)
#define TWAI_RX_TASK_PRIORITY (configMAX_PRIORITIES - 1)
#define UART_TX_TASK_PRIORITY (configMAX_PRIORITIES - 2)

static const char *Timer_TAG = "Timer";
static const char *TX_TASK_TAG = "TX_TASK";
static const char *TWAI_TASK_TAG = "TWAI_TASK";

static TaskHandle_t processing_task = NULL;
static SemaphoreHandle_t sem_done_reading = NULL;
static portMUX_TYPE spinlock = portMUX_INITIALIZER_UNLOCKED;
static portMUX_TYPE uartlock = portMUX_INITIALIZER_UNLOCKED;

gptimer_handle_t gptimer = NULL;

QueueHandle_t uart_tx_queue[2];		      // Two buffers for UART transmit
volatile int active_buffer = 0;
static volatile uint8_t buf_overrun = 0;      // Double buffer overrun flag

TaskHandle_t uart_tx_task_handle;

twai_message_t rx_message = { .identifier = 1,
                                .data_length_code = 3,
                                .data = {0, 85, 170, 0, 0, 0, 0, 0}
                              };


typedef union 
{
   uint32_t u4_input;
   uint8_t  u1_byte_arr[4];
}UN_COMMON_32BIT_TO_4X8BIT_CONVERTER;

// UN_COMMON_32BIT_TO_4X8BIT_CONVERTER un_t_mode_reg;
// un_t_mode_reg.u4_input = input;/*your 32 bit input*/
// 1st byte = un_t_mode_reg.u1_byte_arr[0];
// 2nd byte = un_t_mode_reg.u1_byte_arr[1];
// 3rd byte = un_t_mode_reg.u1_byte_arr[2];
// 4th byte = un_t_mode_reg.u1_byte_arr[3];

// Message struct to wrap strings for queue
typedef struct CAN_Serial_Frame {
  uint8_t sof;
  UN_COMMON_32BIT_TO_4X8BIT_CONVERTER timestamp;
  uint8_t dlc;
  UN_COMMON_32BIT_TO_4X8BIT_CONVERTER msg_id;
  uint8_t payload[8];
  uint8_t eof;
}CAN_Serial_Frame; 

CAN_Serial_Frame CSF = {.sof = 0xAA,
                        .timestamp.u4_input = 100,
                        .dlc = 8,
                        .msg_id.u4_input = 1,
                        .payload = {0, 0, 0, 0, 0, 0, 0, 0},
                        .eof = 0xBB 
                      };




uint8_t serialFrame[] = {
    0xAA, // Start of frame 0
    0xD0, 0x07, 0x00, 0x00, // Placeholder for Timestamp (Little-endian) 1
    0x08, // DLC (Data Length Code) 5
    0x01, 0x00, 0x00, 0x00, // Placeholder for Arbitration ID 6
    0x33, 0x22, 0x33, 0x44, // Placeholder for Payload 10
    0x55, 0x66, 0x77, 0x88,
    0xBB // End of frame 18
  };

/*Timer ISR*/
uint8_t update_flag = 1;
void IRAM_ATTR onTimer() {
  xQueueSend(uart_tx_queue[active_buffer], &rx_message, 0.001/portTICK_PERIOD_MS);
  static uint16_t idx = 0;
  
  BaseType_t task_woken = pdFALSE;
  portENTER_CRITICAL(&spinlock);
  if(update_flag){
    rx_message.data[0]++;
    rx_message.data[1]++;
    rx_message.data[2]++;
  }
  
  if(rx_message.data[0]>84){
    rx_message.data[0] = 0;
    // update_flag = 0;
    }

  if(rx_message.data[1]>170){
    rx_message.data[1] = 85;
    // update_flag = 0;
  }

  if(rx_message.data[2]>254){
    rx_message.data[2] = 170;
    // update_flag = 0;
  }
  active_buffer = 1 - active_buffer;
  portEXIT_CRITICAL(&spinlock);
  xTaskNotifyFromISR(uart_tx_task_handle,0,eNoAction,&task_woken);
  // xTaskNotifyFromISR(processing_task,0,eNoAction,&task_woken);

  if (task_woken == pdTRUE) {
        portYIELD_FROM_ISR(task_woken);
  }
}

// void Data_Update_Task(void *parameters){

//   // Start a timer to run ISR every 1 ms
//   // %%% We move this here so it runs in core 0
//   ESP_LOGI(Timer_TAG, "Create timer handle");
  
//   gptimer_config_t timer_config = {
//       .clk_src = GPTIMER_CLK_SRC_DEFAULT,
//       .direction = GPTIMER_COUNT_UP,
//       .resolution_hz = 1000000, // 1MHz, 1 tick=1us
//   };
//   ESP_ERROR_CHECK(gptimer_new_timer(&timer_config, &gptimer));

//   gptimer_event_callbacks_t cbs = {
//       .on_alarm = onTimer,
//   };
//   ESP_ERROR_CHECK(gptimer_register_event_callbacks(gptimer, &cbs, NULL));

//   ESP_LOGI(Timer_TAG, "Enable timer");
//   ESP_ERROR_CHECK(gptimer_enable(gptimer));

//   ESP_LOGI(Timer_TAG, "Start timer, auto-reload at alarm event");
//   gptimer_alarm_config_t alarm_config = {
//       .reload_count = 0,
//       .alarm_count = 1000, // period = 1ms
//       .flags.auto_reload_on_alarm = true,
//   };

//   ESP_ERROR_CHECK(gptimer_set_alarm_action(gptimer, &alarm_config));
//   ESP_ERROR_CHECK(gptimer_start(gptimer));

//   while(1){

//   }
// }

void timer_init(){
    // Start a timer to run ISR every 1 ms
  // %%% We move this here so it runs in core 0
  ESP_LOGI(Timer_TAG, "Create timer handle");
  
  gptimer_config_t timer_config = {
      .clk_src = GPTIMER_CLK_SRC_DEFAULT,
      .direction = GPTIMER_COUNT_UP,
      .resolution_hz = 1000000, // 1MHz, 1 tick=1us
  };
  ESP_ERROR_CHECK(gptimer_new_timer(&timer_config, &gptimer));

  gptimer_event_callbacks_t cbs = {
      .on_alarm = onTimer,
  };
  ESP_ERROR_CHECK(gptimer_register_event_callbacks(gptimer, &cbs, NULL));

  ESP_LOGI(Timer_TAG, "Enable timer");
  ESP_ERROR_CHECK(gptimer_enable(gptimer));

  ESP_LOGI(Timer_TAG, "Start timer, auto-reload at alarm event");
  gptimer_alarm_config_t alarm_config = {
      .reload_count = 0,
      .alarm_count = 1000, // period = 1ms
      .flags.auto_reload_on_alarm = true,
  };

  ESP_ERROR_CHECK(gptimer_set_alarm_action(gptimer, &alarm_config));
  ESP_ERROR_CHECK(gptimer_start(gptimer));
}


/*TWAI*/
uint8_t driver_installed=0;
void twai_init(){
  twai_general_config_t general_config = TWAI_GENERAL_CONFIG_DEFAULT(TX_GPIO_NUM, RX_GPIO_NUM, TWAI_MODE_NORMAL);
  general_config.tx_queue_len = 1000;
  general_config.rx_queue_len = 1000;

  twai_timing_config_t timing_config = TWAI_TIMING_CONFIG_1MBITS();
  
  // Extended CAN ID filter
  twai_filter_config_t filter=TWAI_FILTER_CONFIG_ACCEPT_ALL();


  //EXTDID_Filter(filter);

    ESP_ERROR_CHECK(twai_driver_install(&general_config, &timing_config, &filter));
    ESP_LOGI(TWAI_TASK_TAG, "Driver installed");
    ESP_ERROR_CHECK(twai_start());
    ESP_LOGI(TWAI_TASK_TAG, "Driver started");
    uint32_t alerts_to_enable = TWAI_ALERT_RX_DATA | TWAI_ALERT_ERR_PASS | TWAI_ALERT_BUS_ERROR | TWAI_ALERT_RX_QUEUE_FULL;
    if (twai_reconfigure_alerts(alerts_to_enable, NULL) == ESP_OK){
        driver_installed = true;
    }
}

static void twai_receive_task(void *arg)
{
  twai_init();
  twai_message_t message;
  BaseType_t xHigherPriorityTaskWoken;
  xHigherPriorityTaskWoken = pdFALSE;
  while(1){

    if (driver_installed){
      uint32_t alerts_triggered;
      twai_status_info_t status_info;

      twai_read_alerts(&alerts_triggered, pdMS_TO_TICKS(1));
      twai_get_status_info(&status_info);

      if (alerts_triggered & TWAI_ALERT_RX_DATA){
        twai_message_t message;
        while (twai_receive(&message, 0) == ESP_OK){
          xQueueSend(uart_tx_queue[active_buffer], &message, 0.001/portTICK_PERIOD_MS);
          xTaskNotify(uart_tx_task_handle,NULL,eNoAction);
        }
      }
    }
  }
}

/*UART*/
void uart_init() {
    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };

    uart_param_config(UART_NUM, &uart_config);
    ESP_ERROR_CHECK( uart_set_pin(UART_NUM, TXD_PIN, RXD_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE) );
    
    // Install the UART driver with a buffer size of 1024 bytes
    ESP_ERROR_CHECK( uart_driver_install(UART_NUM, 1024, 1024*3, 0, NULL, 0) );
    ESP_LOGI(TX_TASK_TAG, "UART Driver Installed");
}

void uart_tx_task(void *parameters){
  uart_init();
  twai_message_t tx_message;
  UN_COMMON_32BIT_TO_4X8BIT_CONVERTER timestamp;
  timestamp.u4_input = 0;
  UN_COMMON_32BIT_TO_4X8BIT_CONVERTER msg_id;
  while (1) {
    // Process all available TWAI messages in the active buffer
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    while(xQueueReceive(uart_tx_queue[active_buffer], &tx_message, portMAX_DELAY)) {
      timestamp.u4_input++;
      // Process the TWAI message and send it over UART
      serialFrame[5] = tx_message.data_length_code;
      msg_id.u4_input = tx_message.identifier;
      for(int i = 0; i<4; i++){
        serialFrame[6+i] = msg_id.u1_byte_arr[i];
        serialFrame[1+i] = timestamp.u1_byte_arr[i];
      }
      uart_write_bytes(UART_NUM,serialFrame, 10);
      for (int i = 0; i < tx_message.data_length_code; i++) {
        serialFrame[10+i] = tx_message.data[i];
        uart_write_bytes(UART_NUM,&serialFrame[10+i], 1);
      }
      uart_write_bytes(UART_NUM,&serialFrame[18], 1);
    }

    // const int txBytes = uart_write_bytes(UART_NUM,(const char *)&CSF, sizeof(CSF));
    // ESP_LOGI(TX_TASK_TAG, "Wrote %d bytes", txBytes);
    // ESP_LOGI(TX_TASK_TAG, "Data Sent: %d",tx_message.data[0]);

    // vTaskDelay(20/portTICK_PERIOD_MS);
  }
}

void app_main(void){

  /*Create two queues for double buffering of UART transmit*/
  uart_tx_queue[0] = xQueueCreate(100, sizeof(twai_message_t));
  uart_tx_queue[1] = xQueueCreate(100, sizeof(twai_message_t));

  /*Create UART Transmit Task*/
  xTaskCreate(uart_tx_task, "uart_tx_task", 1024*6, NULL, UART_TX_TASK_PRIORITY, &uart_tx_task_handle);

  /*Create TWAI Receive Task*/
  // xTaskCreate(twai_receive_task, "twai_receive_task", 1024*6, NULL, TWAI_RX_TASK_PRIORITY, &processing_task);
  timer_init();
  

}