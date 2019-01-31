/*
 * tim3_interrupt.h
 *
 *  Created on: 29 gen 2019
 *      Author: enric
 */

#ifndef TIM3_INTERRUPT_H_
#define TIM3_INTERRUPT_H_
#include "stm32f4xx_hal.h"

volatile int tim3_overflow;
volatile int tim3_flag_overflow;

/**
  * @brief  Increment TIM overflow variable
  * @param  htim pointer to a TIM_HandleTypeDef structure that contains
  *                the configuration information for TIM module.
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim);
/**
  * @brief  Set overflow flag of OC delay elapsed
  * @param  htim pointer to a TIM_HandleTypeDef structure that contains
  *                the configuration information for TIM module.
  */
void HAL_TIM_OC_DelayElapsedCallback(TIM_HandleTypeDef *htim);

#endif /* TIM3_INTERRUPT_H_ */
