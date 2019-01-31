/*
 * tim3_interrupt.c
 *
 *  Created on: 29 gen 2019
 *      Author: enric
 */

#include "tim3_interrupt.h"

/**
  * @brief  Increment TIM overflow variable
  * @param  htim pointer to a TIM_HandleTypeDef structure that contains
  *                the configuration information for TIM module.
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim){
	if(htim->Instance == TIM3)
		tim3_overflow++;
}
/**
  * @brief  Set overflow flag of OC delay elapsed
  * @param  htim pointer to a TIM_HandleTypeDef structure that contains
  *                the configuration information for TIM module.
  */
void HAL_TIM_OC_DelayElapsedCallback(TIM_HandleTypeDef *htim){
	if(htim->Instance == TIM3)
		tim3_flag_overflow=1;
}
