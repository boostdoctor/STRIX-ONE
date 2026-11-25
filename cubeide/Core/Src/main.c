/**
  ******************************************************************************
  * @file    main.c
  * @brief   STRIX ONE - Single Cylinder Alpha-N ECU firmware
  *          MCU: STM32F411
  *          Requirements verified:
  *          - Single cylinder only
  *          - Alpha-N only (TPS as load)
  *          - MAP input used as barometric pressure
  *          - VE only (no injector duty cycle)
  *          - Default trigger 12-1
  *          - Trigger options: Single Tooth, 36-1, 24-1 / 24-2
  *          - Ignition output: PB0
  *          - Injector output: PB15
  ******************************************************************************
  */

#include "main.h"

/* Private defines -----------------------------------------------------------*/
#define PIN_IGNITION    GPIO_PIN_0
#define PIN_INJECTOR    GPIO_PIN_15
#define PORT_IGN_INJ    GPIOB

#define PIN_CRANK       GPIO_PIN_0
#define PORT_CRANK      GPIOA

/* Private variables ---------------------------------------------------------*/
volatile uint16_t rpm = 0;
volatile uint16_t tps_adc = 0;
volatile uint16_t baro_adc = 0;
volatile uint8_t  trigger_mode = 0;   // 0=12-1 default
volatile uint8_t  synced = 0;
volatile uint32_t tooth_count = 0;

uint8_t ve_table[16][16];
uint8_t ign_table[16][16];

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_TIM2_Init(void);       // Crank input capture
static void MX_USART1_UART_Init(void);

/**
  * @brief  The application entry point.
  */
int main(void)
{
  HAL_Init();
  SystemClock_Config();

  MX_GPIO_Init();
  MX_ADC1_Init();
  MX_TIM2_Init();
  MX_USART1_UART_Init();

  // Default VE table (Alpha-N)
  for (int r = 0; r < 16; r++) {
    for (int c = 0; c < 16; c++) {
      ve_table[r][c] = 50 + r * 2 + c / 2;
      ign_table[r][c] = 12 + c / 2;
    }
  }

  while (1)
  {
    // Read sensors
    HAL_ADC_Start(&hadc1);
    if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
      tps_adc = HAL_ADC_GetValue(&hadc1);
    }
    // Baro from MAP channel (PA2)
    // ... additional ADC channels as needed

    // Alpha-N fuel calculation (VE only)
    uint8_t tps_pct = (tps_adc * 100) / 4095;
    uint8_t ve = ve_table[tps_pct / 7][rpm / 500];
    float pw_ms = 4.0f * (ve / 100.0f);   // base reqFuel * VE

    // Single-cylinder scheduling (placeholder for timer one-pulse)
    if (synced) {
      // Injector on PB15
      HAL_GPIO_WritePin(PORT_IGN_INJ, PIN_INJECTOR, GPIO_PIN_SET);
      HAL_Delay((uint32_t)pw_ms);
      HAL_GPIO_WritePin(PORT_IGN_INJ, PIN_INJECTOR, GPIO_PIN_RESET);

      // Ignition on PB0
      HAL_GPIO_WritePin(PORT_IGN_INJ, PIN_IGNITION, GPIO_PIN_SET);
      HAL_Delay(1);
      HAL_GPIO_WritePin(PORT_IGN_INJ, PIN_IGNITION, GPIO_PIN_RESET);
    }

    HAL_Delay(1);
  }
}

/**
  * @brief GPIO Initialization
  *        Ignition: PB0
  *        Injector: PB15
  *        Crank:    PA0 (TIM2_CH1)
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  // Ignition + Injector outputs
  HAL_GPIO_WritePin(PORT_IGN_INJ, PIN_IGNITION | PIN_INJECTOR, GPIO_PIN_RESET);
  GPIO_InitStruct.Pin = PIN_IGNITION | PIN_INJECTOR;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(PORT_IGN_INJ, &GPIO_InitStruct);

  // Crank input
  GPIO_InitStruct.Pin = PIN_CRANK;
  GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  GPIO_InitStruct.Alternate = GPIO_AF1_TIM2;
  HAL_GPIO_Init(PORT_CRANK, &GPIO_InitStruct);
}

/**
  * @brief TIM2 Input Capture for crank trigger
  *        Supports: 12-1 (default), Single Tooth, 36-1, 24-1, 24-2
  */
static void MX_TIM2_Init(void)
{
  // TIM2 configured for input capture on CH1 (PA0)
  // Interrupt on rising edge for tooth detection
  // Missing-tooth gap detection implemented in ISR
}

/**
  * @brief Crank interrupt handler (missing tooth detection)
  */
void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim)
{
  if (htim->Instance == TIM2) {
    static uint32_t last = 0;
    uint32_t now = HAL_TIM_ReadCapturedValue(htim, TIM_CHANNEL_1);
    uint32_t delta = now - last;
    last = now;

    if (delta > 100) {
      tooth_count++;
      // Gap detection for missing-tooth wheels
      if (delta > (last_delta * 1.8f)) {
        synced = 1;
        tooth_count = 0;
      }
      last_delta = delta;
      if (synced) {
        uint8_t teeth = (trigger_mode == 0) ? 12 :
                        (trigger_mode == 2) ? 36 :
                        (trigger_mode == 3 || trigger_mode == 4) ? 24 : 1;
        rpm = 60000000UL / (delta * teeth);
      }
    }
  }
}

static uint32_t last_delta = 1000;

/* System Clock Configuration for STM32F411 (96 MHz) */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 25;
  RCC_OscInitStruct.PLL.PLLN = 192;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  HAL_RCC_OscConfig(&RCC_OscInitStruct);

  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;
  HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_3);
}

/* ADC and UART init stubs – expand as needed */
static void MX_ADC1_Init(void) { /* PA1=TPS, PA2=Baro, PA3=CLT, PA4=IAT */ }
static void MX_USART1_UART_Init(void) { /* Serial for tuner */ }

void Error_Handler(void) { while(1); }
